from state import State
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, AIMessage
from langgraph.types import interrupt, Command
from huggingface_hub import InferenceClient
from maths import get_embedding, cosine_similarity


import os
from dotenv import load_dotenv
load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

HF_API_KEY = os.getenv("HUGGINGFACEHUB_API_TOKEN")

llm = ChatGroq(model = "llama3-70b-8192")

client = InferenceClient(api_key=HF_API_KEY)
model = "sentence-transformers/all-MiniLM-L6-v2"



def chatbot(state: State):

    state["count"] = 0
    topic = state["topic"]

    # Define system prompt
    system_msg = SystemMessage(content=f"""
    You are an evaluation agent, behaving like a human evaluator.
    Your role is to test a learner’s understanding of the topic '{topic}' by asking 5–8 questions one by one.

    Rules:
    - Do NOT give all questions at once.
    - After each user answer, use the similarity score to guide grading:
        * If similarity_score > 0.8 → Full marks (close to 1).
        * 0.6–0.8 → Mostly correct (0.6–0.8).
        * 0.3–0.6 → Partial credit (0.3–0.6).
        * <0.3 → Poor/incorrect (0–0.3).
    - Give clear and constructive feedback after each answer.
    - Always show both the similarity score and the correct answer.
    - Maintain a running total score across all questions.
    - At the end of all questions, normalize the total and provide the learner with a **final score out of 10**.
    - Give a brief performance summary highlighting strengths and areas to improve.
    """)


    if not state["messages"] or not isinstance(state["messages"][0], SystemMessage):
        state["messages"].insert(0, system_msg)

    response = llm.invoke(state["messages"])
    question_text = response.content

    return {"messages": [response], "next_question" :  question_text}


def user_answer(state: State) -> State:
    result = interrupt({
        "user": "Answer the question",
        "question": state["next_question"]
    })


    return {
        "messages": [result["user_answer"]]
    }

def evaluate_answer(state : State):
    last_question = state["next_question"]
    user_answer = state["messages"][-1].content

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an assistant that ONLY answers the explicit question inside the given text. "
            "Ignore any extra wording, instructions, or chit-chat around it. "
            "Give a concise and direct answer in plain text, nothing else."
        ),
        (
            "human",
            "Here is the text containing a question:\n\n{last_question}\n\n"
            "Provide only the answer to the question."
        )
    ])

    system_prompt = prompt.format(last_question = last_question)
    response = llm.invoke(system_prompt) 
    actual_answer = response.content

    user_embedding = get_embedding(user_answer,client=client, model = model)
    actual_embedding = get_embedding(actual_answer, client=client, model = model)

    similarity_score = cosine_similarity(user_embedding, actual_embedding)

    return {"messages" : [AIMessage(content = f"The similarity score between the user's answer and actual_answer is {similarity_score}")]}






