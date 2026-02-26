import os
from dotenv import load_dotenv
load_dotenv()

from typing import List, Dict, Generator, Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.store.memory import InMemoryStore
from redis_store import RedisStore

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables.config import RunnableConfig


class MockModel:
    def __init__(self, temperature=0):
        self.temperature = temperature

    def invoke(self, messages: List[Any]):
        # Very small mock behavior: echo last human message
        last = None
        for m in reversed(messages):
            if hasattr(m, 'content'):
                last = m.content
                break
        content = "[MOCK] " + (last or "Hello")
        return [SystemMessage(content=content)]


class LangGraphEngine:
    def __init__(self):
        # Model: use real ChatOpenAI if key present, otherwise MockModel
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.model = ChatOpenAI(temperature=0)
        else:
            self.model = MockModel()

        self.CLINIC_NAME = "Good Health Clinic"

        self.MODEL_SYSTEM_MESSAGE = (
            "You are a helpful medical assistant for {clinic_name}. "
            "Use the patient's history to provide relevant, personalized appointment scheduling or advice."
            "Patient profile: {history}"
        )

        self.UPDATE_PATIENT_PROFILE_INSTRUCTION = (
            "Update the patient's medical/appointment profile with new information.\n\n"
            "CURRENT PROFILE:\n{history}\n\nANALYZE FOR:\n1. Appointment history (dates, times, no-shows)\n"
            "2. Medical preferences or concerns\n3. Previous diagnoses or treatments\n4. Medication usage or allergies\n5. Follow-up needs\n\n"
            "Focus on verified appointment and medical details only. Summarize key points clearly.\n\n"
            "Update the profile based on this conversation:\n"
        )

        # Build graph
        builder = StateGraph(MessagesState)

        builder.add_node("check_condition", self.check_condition)
        builder.add_node("call_model", self.call_model)
        builder.add_node("handle_emergency", self.handle_emergency)
        builder.add_node("write_memory", self.write_memory)

        builder.add_edge(START, "check_condition")

        builder.add_conditional_edges(
            "check_condition",
            lambda state: state["decision"],
            {
                "emergency_route": "handle_emergency",
                "regular_route": "call_model",
                "end": END,
            },
        )

        builder.add_edge("handle_emergency", "write_memory")
        builder.add_edge("call_model", "write_memory")
        builder.add_edge("write_memory", END)

        # stores: prefer Redis when REDIS_URL provided
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            try:
                self.across_thread_memory = RedisStore(redis_url)
            except Exception:
                self.across_thread_memory = InMemoryStore()
        else:
            self.across_thread_memory = InMemoryStore()
        self.within_thread_memory = MemorySaver()

        self.graph = builder.compile(checkpointer=self.within_thread_memory, store=self.across_thread_memory)

    def check_condition(self, state: MessagesState, config: RunnableConfig = None, store: InMemoryStore = None):
        user_msg = state["messages"][-1].content.lower()
        if "emergency" in user_msg:
            return {"decision": "emergency_route"}
        return {"decision": "regular_route"}

    def handle_emergency(self, state: MessagesState, config: RunnableConfig = None, store: InMemoryStore = None):
        return {
            "messages": [
                SystemMessage(content="We’ve detected an emergency. Please contact emergency services immediately or call our 24/7 urgent line: +43 00 00 00."),
            ]
        }

    def call_model(self, state: MessagesState, config: RunnableConfig = None, store: InMemoryStore = None):
        patient_id = config["configurable"]["patient_id"]
        namespace = ("patient_interactions", patient_id)
        key = "patient_data_memory"

        mem_store = store if store is not None else self.across_thread_memory
        memory = mem_store.get(namespace, key)
        history = memory.value.get(key) if memory and memory.value else "No existing patient profile found."

        system_msg = self.MODEL_SYSTEM_MESSAGE.format(history=history, clinic_name=self.CLINIC_NAME)

        response = self.model.invoke([SystemMessage(content=system_msg)] + state["messages"])
        return {"messages": response}

    def write_memory(self, state: MessagesState, config: RunnableConfig = None, store: InMemoryStore = None):
        patient_id = config["configurable"]["patient_id"]
        namespace = ("patient_interactions", patient_id)
        key = "patient_data_memory"
        mem_store = store if store is not None else self.across_thread_memory
        memory = mem_store.get(namespace=namespace, key=key)
        history = memory.value.get(key) if memory and memory.value else "No existing history."

        system_msg = self.UPDATE_PATIENT_PROFILE_INSTRUCTION.format(history=history)
        new_insights = self.model.invoke([SystemMessage(content=system_msg)] + state["messages"])

        # Save updated profile text; new_insights may be a list of messages
        text = ""
        if isinstance(new_insights, list):
            text = "\n".join([m.content for m in new_insights if hasattr(m, 'content')])
        elif hasattr(new_insights, 'content'):
            text = new_insights.content

        mem_store.put(namespace, key, {key: text})

    def stream_chat(self, user_messages: List[Dict[str, str]], patient_id: str = "1", thread_id: str = "1"):
        """Stream conversation chunks. Yields plain text chunks (strings).

        user_messages: list of dicts like {"role": "human", "content": "..."}
        """
        # Build HumanMessage list
        msgs = [HumanMessage(content=m["content"]) for m in user_messages]

        # If any incoming user message mentions 'emergency', mark the whole exchange
        emergency_flag = any([('emergency' in (m.get('content','') or '').lower()) for m in user_messages])

        config = {"configurable": {"thread_id": thread_id, "patient_id": patient_id}}

        for chunk in self.graph.stream({"messages": msgs}, config, stream_mode="values"):
            # yield dict with text content and emergency flag
            out = None
            try:
                out_msg = chunk["messages"][-1]
                out = getattr(out_msg, 'content', str(out_msg))
            except Exception:
                out = str(chunk)
            yield {"chunk": out, "emergency": emergency_flag}

    def get_patient_profile(self, patient_id: str):
        namespace = ("patient_interactions", patient_id)
        key = "patient_data_memory"
        memory = self.across_thread_memory.get(namespace, key)
        if memory and memory.value:
            return memory.value.get(key)
        return None
