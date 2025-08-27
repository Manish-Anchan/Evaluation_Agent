import streamlit as st
import os
from dotenv import load_dotenv
from langgraph.types import Command
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage
from state import State
from nodes import chatbot, user_answer, evaluate_answer

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="AI Evaluation Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# FIXED CSS: force readable text color inside boxes and preserve whitespace
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .question-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
        color: #111111 !important;
        line-height: 1.5;
        font-size: 1rem;
        white-space: pre-wrap;
    }
    .question-box * { color: #111111 !important; }
    .answer-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #28a745;
        margin: 1rem 0;
        color: #111111 !important;
        white-space: pre-wrap;
    }
    .score-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #ffc107;
        margin: 1rem 0;
        color: #111111 !important;
        white-space: pre-wrap;
    }
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #0d5aa7;
    }
</style>
""", unsafe_allow_html=True)

def initialize_graph():
    """Initialize the LangGraph with checkpointer"""
    checkpointer = InMemorySaver()
    graph_builder = StateGraph(State)
    
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("user_answer", user_answer)
    graph_builder.add_node("evaluate_answer", evaluate_answer)
    
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", "user_answer")
    graph_builder.add_edge("user_answer", "evaluate_answer")
    graph_builder.add_edge("evaluate_answer", END)
    
    return graph_builder.compile(checkpointer=checkpointer)

def main():
    # Initialize session state
    if 'graph' not in st.session_state:
        st.session_state.graph = initialize_graph()
    
    if 'config' not in st.session_state:
        st.session_state.config = {"configurable": {"thread_id": "1"}}
    
    if 'current_question' not in st.session_state:
        st.session_state.current_question = ""
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'evaluation_started' not in st.session_state:
        st.session_state.evaluation_started = False
    
    if 'waiting_for_answer' not in st.session_state:
        st.session_state.waiting_for_answer = False
    
    if 'question_count' not in st.session_state:
        st.session_state.question_count = 0
    
    # Main header
    st.markdown('<h1 class="main-header">🤖 AI Evaluation Agent</h1>', unsafe_allow_html=True)
    
    # Sidebar for settings and info
    with st.sidebar:
        st.header("📋 Settings")
        
        # --- CHANGED: topic input is now a free text field instead of a selectbox ---
        topic_input_default = st.session_state.get("selected_topic", "Machine Learning")
        topic = st.text_input(
            "Choose Topic (type any topic):",
            value=topic_input_default,
            placeholder="Enter topic (e.g., Machine Learning)",
            key="selected_topic"
        )
        # fallback if user leaves it empty
        if not topic or not topic.strip():
            topic = "General"
        
        st.markdown("---")
        st.header("ℹ️ How it works")
        st.markdown("""
        1. **Select a topic** from the dropdown
        2. **Start the evaluation** by clicking the button
        3. **Answer questions** one by one
        4. **Get instant feedback** with similarity scores
        5. **Receive final score** out of 10 at the end
        """)
        
        st.markdown("---")
        st.header("📊 Progress")
        if st.session_state.question_count > 0:
            st.metric("Questions Answered", st.session_state.question_count)
        
        # Reset button
        if st.button("🔄 Reset Session", type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if not st.session_state.evaluation_started:
            st.markdown("### Welcome to the AI Evaluation Agent! 🎯")
            st.markdown(f"""
            Ready to test your knowledge on **{topic}**? 
            
            This AI agent will ask you 5-8 questions to evaluate your understanding. 
            You'll receive immediate feedback and a final score out of 10.
            """)
            
            if st.button("🚀 Start Evaluation", type="primary", use_container_width=True):
                st.session_state.evaluation_started = True
                st.session_state.current_topic = topic
                
                # Initialize the conversation
                try:
                    result = st.session_state.graph.invoke(
                        {"messages": [{"role": "user", "content": "start"}], "topic": topic},
                        st.session_state.config
                    )
                    # SAFER: use get and fallback to help debugging if key missing
                    st.session_state.current_question = str(result.get("next_question", "No question returned. (check graph result keys)"))
                    st.session_state.waiting_for_answer = True
                    st.session_state.question_count += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"Error starting evaluation: {str(e)}")
        
        elif st.session_state.waiting_for_answer:
            # Display current question (use pre to preserve formatting)
            st.markdown("### 📝 Current Question")
            st.markdown(
                f'<div class="question-box"><pre style="margin:0; font-family: inherit;">{st.session_state.current_question}</pre></div>', 
                unsafe_allow_html=True
            )
            
            # Answer input
            with st.form("answer_form", clear_on_submit=True):
                user_answer = st.text_area(
                    "Your Answer:",
                    placeholder="Type your answer here...",
                    height=150,
                    key="answer_input"
                )
                
                col_submit, col_skip = st.columns([3, 1])
                with col_submit:
                    submit_answer = st.form_submit_button("Submit Answer", type="primary", use_container_width=True)
                with col_skip:
                    skip_question = st.form_submit_button("Skip", type="secondary", use_container_width=True)
                
                if submit_answer and user_answer.strip():
                    try:
                        # Process the answer
                        user_answer_msg = HumanMessage(content=user_answer)
                        resumed_result = st.session_state.graph.invoke(
                            Command(resume={"user_answer": user_answer_msg}),
                            config=st.session_state.config
                        )
                        
                        # Store conversation history (safely try to extract evaluation)
                        evaluation_text = "No evaluation available"
                        try:
                            if resumed_result.get("messages"):
                                evaluation_text = resumed_result["messages"][-1].content
                        except Exception:
                            evaluation_text = str(resumed_result)
                        
                        st.session_state.conversation_history.append({
                            "question": st.session_state.current_question,
                            "user_answer": user_answer,
                            "evaluation": evaluation_text
                        })
                        
                        st.session_state.waiting_for_answer = False
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error processing answer: {str(e)}")
                
                elif skip_question:
                    st.session_state.conversation_history.append({
                        "question": st.session_state.current_question,
                        "user_answer": "Skipped",
                        "evaluation": "Question was skipped"
                    })
                    st.session_state.waiting_for_answer = False
                    st.rerun()
        
        else:
            st.markdown("### 🔄 Processing...")
            st.info("Generating next question or finishing evaluation...")
            
            # Auto-continue to next question or finish
            try:
                result = st.session_state.graph.invoke(
                    {"messages": [{"role": "user", "content": "continue"}], "topic": st.session_state.current_topic},
                    st.session_state.config
                )
                
                if "next_question" in result and result["next_question"]:
                    st.session_state.current_question = str(result["next_question"])
                    st.session_state.waiting_for_answer = True
                    st.session_state.question_count += 1
                    st.rerun()
                else:
                    st.session_state.evaluation_started = False
                    st.success("Evaluation completed!")
                    
            except Exception as e:
                st.error(f"Error continuing evaluation: {str(e)}")
                st.session_state.evaluation_started = False
    
    with col2:
        if st.session_state.conversation_history:
            st.markdown("### 📈 Conversation History")
            
            for i, exchange in enumerate(st.session_state.conversation_history):
                with st.expander(f"Question {i+1}", expanded=(i == len(st.session_state.conversation_history)-1)):
                    st.markdown(f"**Q:** {exchange['question']}")
                    st.markdown(f'<div class="answer-box"><strong>Your Answer:</strong> {exchange["user_answer"]}</div>', 
                               unsafe_allow_html=True)
                    st.markdown(f'<div class="score-box"><strong>Evaluation:</strong> {exchange["evaluation"]}</div>', 
                               unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "Built with ❤️ using Streamlit and LangGraph | "
        "Powered by Groq LLM and HuggingFace Embeddings"
    )

if __name__ == "__main__":
    main()
