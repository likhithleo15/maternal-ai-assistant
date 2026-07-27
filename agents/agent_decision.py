"""
Maternal AI Agent Decision System
Stripped to: CONVERSATION_AGENT + RAG_AGENT only
Powered by Gemini (free tier)
"""

import json
import os
import re
import ast
from typing import Dict, List, Optional, Any, Union, Annotated, TypedDict
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import MessagesState, StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

from agents.guardrails.local_guardrails import LocalGuardrails
from config import Config

# Lazily import MedicalRAG to avoid import errors on serverless deployment
try:
    from agents.rag_agent import MedicalRAG
except Exception:
    MedicalRAG = None

load_dotenv()

config = Config()
memory = MemorySaver()


def get_thread_config(mother_id: str = "default") -> dict:
    return {"configurable": {"thread_id": mother_id}}


# Keep backward compat
thread_config = get_thread_config("maternal_main")


MATERNAL_DECISION_PROMPT = """You are a routing system for a maternal health AI assistant.
Decide which agent should handle the user's message.

Available agents:
1. CONVERSATION_AGENT - For: greetings, general pregnancy questions, explaining sensor alerts, 
   emotional support, nutrition advice, lifestyle questions, interpreting what flags mean, 
   any general chat about pregnancy or motherhood.
2. RAG_AGENT - For: specific clinical questions that need information from medical guidelines,
   detailed questions about conditions (chorioamnionitis, fetal distress, preeclampsia, IUGR),
   sensor threshold explanations, detailed protocol questions, "what does X mean medically".

Guidelines:
- Default to CONVERSATION_AGENT for most questions
- Use RAG_AGENT only when the question needs specific medical knowledge from guidelines
- If unsure, use CONVERSATION_AGENT

Respond ONLY in this exact JSON format (no markdown, no extra text):
{{"agent": "CONVERSATION_AGENT", "reasoning": "brief reason", "confidence": 0.95}}
or
{{"agent": "RAG_AGENT", "reasoning": "brief reason", "confidence": 0.90}}
"""

MATERNAL_CONVERSATION_PROMPT = """You are MaternaAI, a warm and knowledgeable maternal health AI assistant 
built for pregnant women in India. You support women through their pregnancy journey by:

- Answering questions about pregnancy symptoms, nutrition, and wellness
- Explaining what sensor readings and health alerts mean in simple terms
- Providing emotional support and reassurance
- Guiding mothers on when to seek medical help
- Responding in the SAME LANGUAGE as the user (Kannada, Hindi, English, or any other language)

SENSOR DATA (if available):
{sensor_context}

CONVERSATION HISTORY:
{chat_history}

USER'S QUESTION: {user_input}

IMPORTANT RULES:
1. Always respond in the same language the user wrote in
2. Be warm, caring, and non-alarming unless the situation is urgent
3. For CRITICAL sensor alerts, always urge immediate hospital visit
4. Never diagnose — only explain and guide
5. Keep responses concise but complete
6. If sensor data shows active flags, acknowledge them naturally

MaternaAI Response:"""


def _clean_text_content(content: Any) -> str:
    """Utility to clean stringified dictionary output or list structures from LLM messages."""
    if not content:
        return ""

    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, dict) and "text" in block:
                text_parts.append(block["text"])
            elif isinstance(block, str):
                text_parts.append(block)
        return "".join(text_parts)

    text_str = str(content)

    if text_str.startswith("[{") or "'text':" in text_str or '"text":' in text_str:
        try:
            parsed = ast.literal_eval(text_str)
            if isinstance(parsed, list):
                return "".join(
                    item.get("text", "") for item in parsed if isinstance(item, dict)
                )
        except Exception:
            pass

        match = re.search(r"['\"]text['\"]\s*:\s*['\"](.*?)['\"](?:\s*\}|\s*,)", text_str, re.DOTALL)
        if match:
            return match.group(1).replace("\\n", "\n").replace("\\'", "'")

    return text_str


class AgentState(MessagesState):
    agent_name: Optional[str]
    current_input: Optional[Union[str, Dict]]
    output: Optional[Union[str, AIMessage]]
    needs_human_validation: bool
    retrieval_confidence: float
    bypass_routing: bool
    insufficient_info: bool
    sensor_context: Optional[str]


class AgentDecision(TypedDict):
    agent: str
    reasoning: str
    confidence: float


def create_agent_graph():
    guardrails = LocalGuardrails(config.rag.llm)
    decision_model = config.agent_decision.llm
    json_parser = JsonOutputParser(pydantic_object=AgentDecision)

    decision_prompt = ChatPromptTemplate.from_messages([
        ("system", MATERNAL_DECISION_PROMPT),
        ("human", "{input}")
    ])
    decision_chain = decision_prompt | decision_model | json_parser

    def analyze_input(state: AgentState) -> AgentState:
        current_input = state["current_input"]
        input_text = current_input if isinstance(current_input, str) else current_input.get("text", "")

        if input_text:
            is_allowed, message = guardrails.check_input(input_text)
            if not is_allowed:
                return {
                    **state,
                    "messages": message,
                    "agent_name": "INPUT_GUARDRAILS",
                    "bypass_routing": True
                }
        return {**state, "bypass_routing": False}

    def check_if_bypassing(state: AgentState) -> str:
        if state.get("bypass_routing", False):
            return "apply_guardrails"
        return "route_to_agent"

    def route_to_agent(state: AgentState) -> Dict:
        messages = state["messages"]
        current_input = state["current_input"]
        input_text = current_input if isinstance(current_input, str) else current_input.get("text", "")

        recent_context = ""
        for msg in messages[-6:]:
            content_str = _clean_text_content(msg.content)
            if isinstance(msg, HumanMessage):
                recent_context += f"User: {content_str}\n"
            elif isinstance(msg, AIMessage):
                recent_context += f"Assistant: {content_str}\n"

        decision_input = f"""User query: {input_text}

Recent conversation:
{recent_context}

Which agent should handle this?"""

        try:
            decision = decision_chain.invoke({"input": decision_input})
            print(f"[ROUTER] → {decision['agent']} (confidence: {decision.get('confidence', 0):.2f})")
        except Exception as e:
            print(f"[ROUTER] Error: {e}, defaulting to CONVERSATION_AGENT")
            decision = {"agent": "CONVERSATION_AGENT", "confidence": 0.9}

        updated_state = {**state, "agent_name": decision["agent"]}
        return {"agent_state": updated_state, "next": decision["agent"]}

    def run_conversation_agent(state: AgentState) -> AgentState:
        print("[CONVERSATION_AGENT] Processing...")
        messages = state["messages"]
        current_input = state["current_input"]
        sensor_context = state.get("sensor_context", "No live sensor data available.")

        input_text = current_input if isinstance(current_input, str) else current_input.get("text", "")

        recent_context = ""
        for msg in messages:
            content_str = _clean_text_content(msg.content)
            if isinstance(msg, HumanMessage):
                recent_context += f"User: {content_str}\n"
            elif isinstance(msg, AIMessage):
                recent_context += f"Assistant: {content_str}\n"

        prompt = MATERNAL_CONVERSATION_PROMPT.format(
            sensor_context=sensor_context or "No live sensor data available.",
            chat_history=recent_context or "No previous conversation.",
            user_input=input_text
        )

        try:
            response = config.conversation.llm.invoke(prompt)
            raw_content = response.content if hasattr(response, 'content') else str(response)
            response_text = _clean_text_content(raw_content)
        except Exception as e:
            response_text = f"I'm sorry, I encountered an error. Please try again. ({str(e)})"

        return {
            **state,
            "output": AIMessage(content=response_text),
            "agent_name": "CONVERSATION_AGENT"
        }

    def run_rag_agent(state: AgentState) -> AgentState:
        print("[RAG_AGENT] Processing...")
        if MedicalRAG is None:
            print("[RAG_AGENT] MedicalRAG not available. Falling back to CONVERSATION_AGENT.")
            return run_conversation_agent(state)

        try:
            rag_agent = MedicalRAG(config)
        except Exception as e:
            print(f"[RAG_AGENT] Initialization error: {e}. Falling back to CONVERSATION_AGENT.")
            return run_conversation_agent(state)

        messages = state["messages"]
        query = state["current_input"]
        sensor_context = state.get("sensor_context", "")

        recent_context = ""
        for msg in messages[-config.rag.context_limit:]:
            content_str = _clean_text_content(msg.content)
            if isinstance(msg, HumanMessage):
                recent_context += f"User: {content_str}\n"
            elif isinstance(msg, AIMessage):
                recent_context += f"Assistant: {content_str}\n"

        # Inject sensor context into query for better retrieval
        augmented_query = query
        if sensor_context and sensor_context != "No live sensor data available.":
            augmented_query = f"{query}\n\nCurrent sensor context: {sensor_context}"

        try:
            response = rag_agent.process_query(augmented_query, chat_history=recent_context)
            retrieval_confidence = response.get("confidence", 0.0)
            response_content = response["response"]
            raw_text = response_content.content if hasattr(response_content, 'content') else str(response_content)
            response_text = _clean_text_content(raw_text)
        except Exception as e:
            print(f"[RAG_AGENT] Error: {e}")
            return {
                **state,
                "output": AIMessage(content=""),
                "retrieval_confidence": 0.0,
                "agent_name": "RAG_AGENT",
                "insufficient_info": True
            }

        insufficient_info = any(phrase in response_text.lower() for phrase in [
            "don't have enough information",
            "not enough information",
            "insufficient information",
            "cannot answer",
            "unable to answer",
            "i don't know"
        ])

        print(f"[RAG_AGENT] Confidence: {retrieval_confidence:.2f}, Insufficient: {insufficient_info}")

        response_output = AIMessage(content=response_text) if retrieval_confidence >= config.rag.min_retrieval_confidence else AIMessage(content="")

        return {
            **state,
            "output": response_output,
            "needs_human_validation": False,
            "retrieval_confidence": retrieval_confidence,
            "agent_name": "RAG_AGENT",
            "insufficient_info": insufficient_info
        }

    def confidence_based_routing(state: AgentState) -> str:
        low_confidence = state.get("retrieval_confidence", 0.0) < config.rag.min_retrieval_confidence
        insufficient = state.get("insufficient_info", False)
        if low_confidence or insufficient:
            print("[RAG_AGENT] Low confidence → falling back to CONVERSATION_AGENT")
            return "CONVERSATION_AGENT"
        return "check_validation"

    def handle_human_validation(state: AgentState) -> Dict:
        return {"agent_state": state, "next": END}

    def apply_output_guardrails(state: AgentState) -> AgentState:
        output = state.get("output")
        current_input = state.get("current_input")

        if not output or not isinstance(output, (str, AIMessage)):
            return state

        output_text = output if isinstance(output, str) else output.content
        output_text = _clean_text_content(output_text)
        
        if not output_text:
            return state

        input_text = current_input if isinstance(current_input, str) else (current_input.get("text", "") if isinstance(current_input, dict) else "")

        try:
            sanitized_output = guardrails.check_output(output_text, input_text)
        except Exception:
            sanitized_output = output_text

        sanitized_message = AIMessage(content=_clean_text_content(sanitized_output))
        return {**state, "messages": [sanitized_message], "output": sanitized_message}

    # Build the graph
    workflow = StateGraph(AgentState)

    workflow.add_node("analyze_input", analyze_input)
    workflow.add_node("route_to_agent", route_to_agent)
    workflow.add_node("CONVERSATION_AGENT", run_conversation_agent)
    workflow.add_node("RAG_AGENT", run_rag_agent)
    workflow.add_node("check_validation", handle_human_validation)
    workflow.add_node("apply_guardrails", apply_output_guardrails)

    workflow.set_entry_point("analyze_input")

    workflow.add_conditional_edges(
        "analyze_input",
        check_if_bypassing,
        {"apply_guardrails": "apply_guardrails", "route_to_agent": "route_to_agent"}
    )

    workflow.add_conditional_edges(
        "route_to_agent",
        lambda x: x["next"],
        {"CONVERSATION_AGENT": "CONVERSATION_AGENT", "RAG_AGENT": "RAG_AGENT"}
    )

    workflow.add_edge("CONVERSATION_AGENT", "check_validation")
    workflow.add_conditional_edges("RAG_AGENT", confidence_based_routing, {
        "CONVERSATION_AGENT": "CONVERSATION_AGENT",
        "check_validation": "check_validation"
    })

    workflow.add_conditional_edges(
        "check_validation",
        lambda x: x["next"],
        {END: "apply_guardrails"}
    )
    workflow.add_edge("apply_guardrails", END)

    return workflow.compile(checkpointer=memory)


def init_agent_state() -> AgentState:
    return {
        "messages": [],
        "agent_name": None,
        "current_input": None,
        "output": None,
        "needs_human_validation": False,
        "retrieval_confidence": 0.0,
        "bypass_routing": False,
        "insufficient_info": False,
        "sensor_context": None
    }


def process_query(query: Union[str, Dict], mother_id: str = "maternal_main", sensor_context: str = None) -> dict:
    graph = create_agent_graph()
    state = init_agent_state()
    state["current_input"] = query
    state["sensor_context"] = sensor_context or "No live sensor data available."

    query_text = query if isinstance(query, str) else query.get("text", "")
    state["messages"] = [HumanMessage(content=query_text)]

    thread = get_thread_config(mother_id)
    result = graph.invoke(state, thread)

    if len(result["messages"]) > config.max_conversation_history:
        result["messages"] = result["messages"][-config.max_conversation_history:]

    return result