from typing import Annotated, TypedDict
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.tools import create_retriever_tool
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from config import settings

# 1. Initialize Vector Store Retriever
embeddings = OpenAIEmbeddings(
    model=settings.embedding_model, api_key=settings.openai_api_key
)
vector_store = Chroma(
    persist_directory=settings.chroma_persist_dir, embedding_function=embeddings
)

# k=2 keeps the context window lean since we have highly dense, specific records
retriever = vector_store.as_retriever(search_kwargs={"k": 2})

# 2. Create the RAG Tool
retriever_tool = create_retriever_tool(
    retriever,
    "life_insurance_knowledge_base",
    "ALWAYS use this tool first when asked about life insurance policies, benefits, riders, claims, or eligibility. Do not attempt to answer from memory.",
)
tools = [retriever_tool]


# 3. Define the Agent State
class State(TypedDict):
    # `add_messages` ensures the conversational history is appended, not overwritten
    messages: Annotated[list, add_messages]


# 4. Initialize the LLM
llm = ChatOpenAI(
    model=settings.chat_model,
    temperature=0,  # 0 ensures factual, deterministic answers
    api_key=settings.openai_api_key,
)
llm_with_tools = llm.bind_tools(tools)


# 5. Define the Reasoning Node
def chatbot(state: State):
    system_message = {
        "role": "system",
        "content": (
            "You are a helpful, professional Life Insurance Support Assistant. "
            "Use the 'life_insurance_knowledge_base' tool to answer user inquiries accurately. "
            "When you use the tool, seamlessly integrate the ACORD terminology into a natural, easy-to-understand response. "
            "If a user asks something completely unrelated to life insurance, politely steer the conversation back. "
            "If the answer isn't in your knowledge base, admit that you don't have that specific information."
        ),
    }
    messages = [system_message] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# 6. Build the LangGraph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=tools))

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")

# 7. Compile with Memory Checkpointer
memory = MemorySaver()
agent_app = graph_builder.compile(checkpointer=memory)
