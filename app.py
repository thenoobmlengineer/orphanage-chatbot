# app.py
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from prompts import (
    FINANCIAL_ADVISOR_PROMPT,
    CAREER_COUNSELLOR_PROMPT,
    LEADERSHIP_SKILLS_PROMPT,
)
from chatbot_graph import load_chat_history, save_chat_history
from dotenv import load_dotenv  # ← IMPORTANT: Add this
import os

# Load environment variables from .env file
load_dotenv()  # ← This loads your OPENAI_API_KEY

# Optional: Check if key is loaded (for debugging – you can remove later)
if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ OPENAI_API_KEY not found! Please check your .env file.")
    st.stop()

# Page config
st.set_page_config(page_title="Rahbar", page_icon="🌟")
st.title("Rahbar")
st.write("Hi kids! I'm your friendly helper. Choose a mode and let's learn together!")

# Initialize session state
if "mode" not in st.session_state:
    st.session_state.mode = None

if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()  # Safe load even if file empty/corrupt

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Mode selection
if st.session_state.mode is None:
    st.write("### Pick what you want to learn today!")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💰 Financial Advisor", use_container_width=True):
            st.session_state.mode = "Financial Advisor"
            st.rerun()
    with col2:
        if st.button("🚀 Career Counsellor", use_container_width=True):
            st.session_state.mode = "Career Counsellor"
            st.rerun()
    with col3:
        if st.button("👑 Leadership Skills", use_container_width=True):
            st.session_state.mode = "Leadership Skills"
            st.rerun()
else:
    st.success(f"**Mode: {st.session_state.mode}**")

    # Chat input
    if user_input := st.chat_input("Type your message here... 😊"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate response with streaming
        with st.chat_message("assistant"):
            with st.spinner("Thinking... 🤔"):
                message_placeholder = st.empty()

                # Select correct prompt
                prompt_template = {
                    "Financial Advisor": FINANCIAL_ADVISOR_PROMPT,
                    "Career Counsellor": CAREER_COUNSELLOR_PROMPT,
                    "Leadership Skills": LEADERSHIP_SKILLS_PROMPT,
                }[st.session_state.mode]

                # Build history string (exclude current user message)
                history = "\n".join(
                    [f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages[:-1]]
                )

                # Format the full prompt
                full_prompt = PromptTemplate.from_template(prompt_template).format(
                    user_message=user_input, history=history
                )

                # Call GPT-4o-mini with streaming
                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.8, streaming=True)
                full_response = ""
                for chunk in llm.stream([{"role": "user", "content": full_prompt}]):
                    full_response += chunk.content
                    message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)

        # Save assistant response
        st.session_state.messages.append({"role": "assistant", "content": full_response})

        # Persist to file
        save_chat_history(st.session_state.messages)

# Sidebar controls
with st.sidebar:
    st.write("### Options")
    if st.button("🔄 Start New Chat (Clear Everything)"):
        st.session_state.mode = None
        st.session_state.messages = []
        if os.path.exists("history.json"):
            os.remove("history.json")
        st.rerun()

    st.write(f"Total messages: {len(st.session_state.messages)}")
    st.caption("Rahbar for kids")