from state import State
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
import google.generativeai as genai

import os
from dotenv import load_dotenv
load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

llm = ChatGroq(model = "llama3-70b-8192")



def chatbot(state: State):

    state["count"] = 0
    topic = state["topic"]

    # Define system prompt
    system_msg = SystemMessage(content=f"""
    You are an evaluation agent, behaving like a human evaluator.
    Your role is to test a learner’s understanding of the topic '{topic}' by asking 5–8 questions one by one.

    Rules:
    - Do NOT give all questions at once.
    - After each user answer, evaluate whether it is correct, partially correct, or incorrect.
    - Give clear and constructive feedback after each answer.
    - Assign a score for each answer on a flexible scale between 0 and 1 
    (e.g., 1 = fully correct, 0.8 = mostly correct, 0.6 = partially correct, 0.3 = poor attempt, 0 = wrong).
    - Maintain a running total score across all questions.
    - At the end of all questions, normalize the total and provide the learner with a **final score out of 10**.
    - Give a brief performance summary highlighting strengths and areas to improve. 
    """)

    # ✅ If no system message yet, inject it
    if not state["messages"] or not isinstance(state["messages"][0], SystemMessage):
        state["messages"].insert(0, system_msg)

    response = llm.invoke(state["messages"])
    question_text = response.content

    return {"messages": [response], "next_question" :  question_text}


def user_asnwer(state : State):
    user_asnwer = input("enter ")
    return {"messages" : [""]}


def evaluate_answer(state : State):
    ""