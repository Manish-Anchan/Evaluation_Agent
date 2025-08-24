from langgraph.types import interrupt, Command
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel
from typing import List, Annotated
from langgraph.checkpoint.memory import InMemorySaver
from state import State
from nodes import chatbot, user_answer, evaluate_answer
import os
from dotenv import load_dotenv
load_dotenv()
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")

checkpointer = InMemorySaver()
config = {"configurable": {"thread_id": "1"}}
graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("user_answer", user_answer)
graph_builder.add_node("evaluate_answer", evaluate_answer)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "user_answer")
graph_builder.add_edge("user_answer", "evaluate_answer")
graph_builder.add_edge("evaluate_answer", END)



print("Welcome to the Evaluation Agent! (type 'exit' to quit)\n")
graph = graph_builder.compile(checkpointer=checkpointer)


while True:
    
    # initial input

    result = graph.invoke({"messages": [{"role": "user", "content": "start"}], "topic": "Machine Learning"},config)

    
    print(result["next_question"])


    input_answer = input("Enter : ")
    user_answer_input = HumanMessage(content=input_answer)
    resumed_result = graph.invoke(
        Command(resume={"user_answer": user_answer_input}),
        config=config
    )
