from typing import Annotated, TypedDict

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.tools import create_retriever_tool
from langchain_core.messages import trim_messages
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from config import settings

embeddings = OpenAIEmbeddings(
    model=settings.embedding_model, api_key=settings.openai_api_key
)

vector_store = Chroma(
    persist_directory=settings.chroma_persist_dir, embedding_function=embeddings
)

retriever = vector_store.as_retriever(search_kwargs={"k": 2})

retriever_tool = create_retriever_tool(
    retriever,
    "life_insurance_knowledge_base",
    "ALWAYS use this tool first when asked about life insurance policies, benefits, riders, claims, or eligibility. Do not attempt to answer from memory.",
)
tools = [retriever_tool]


class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = ChatOpenAI(
    model=settings.chat_model,
    temperature=0,
    max_tokens=250,
    api_key=settings.openai_api_key,
)
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    system_message = {
        "role": "system",
        "content": (
            "You are an expert Life Insurance Support Assistant. Your primary directive is accuracy.\n\n"
            "CORE RULES:\n"
            "1. STRICT GROUNDING: ALWAYS use the 'life_insurance_knowledge_base' tool first for any policy, claims, or eligibility questions. Do NOT answer from prior training data.\n"
            "2. ZERO HALLUCINATION: If the tool does not return the answer, you must state: 'I do not have that specific information in my current knowledge base.' Do not guess.\n"
            "3. PROFESSIONAL TONE: Seamlessly integrate ACORD terminology into your responses, but ensure the final output is easy for a layman to understand.\n"
            "4. BOUNDARIES: If a user asks about software engineering, coding, or anything outside of life insurance, politely decline and steer the conversation back to insurance."
        ),
    }

    messages_with_system = [system_message] + state["messages"]

    trimmed_messages = trim_messages(
        messages_with_system,
        max_tokens=2000,
        strategy="last",
        token_counter=llm,
        include_system=True,
    )

    response = llm_with_tools.invoke(trimmed_messages)
    return {"messages": [response]}


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=tools))

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")

memory = MemorySaver()
agent_app = graph_builder.compile(checkpointer=memory)
