from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from pydantic import BaseModel
from typing import List, Annotated
from langgraph.checkpoint.memory import MemorySaver
from state import State
from nodes import chatbot, user_asnwer

checkpointer = MemorySaver()
config = {"configurable": {"thread_id": "1"}}
graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("user_answer", user_asnwer)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "user_answer")
graph_builder.add_edge("user_answer", END)

graph = graph_builder.compile(checkpointer=checkpointer, interrupt_before=["user_answer"])

print("Welcome to the Evaluation Agent! (type 'exit' to quit)\n")

# initial input
user_input = input("You: ")

while user_input.lower() != "exit":
    events = graph.stream(
        {"messages": [{"role": "user", "content": user_input}], "topic": "Machine Learning"},
        config,
        stream_mode="values",
    )
    for event in events:
        event["messages"][-1].pretty_print()

    # ask for next user response
    user_input = input("You: ")
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}], "topic": "Machine Learning"},
        config,
        stream_mode="values"):
        event["messages"][-1].pretty_print()