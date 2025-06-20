import uuid
import streamlit as st
import requests

def get_thread_id():
    if 'thread_id' not in st.session_state:
        st.session_state['thread_id'] = str(uuid.uuid4())
    return st.session_state['thread_id']

# --- Page Configuration ---
st.set_page_config(
    page_title="Agentic Ticket System",
    page_icon=":robot_face:",
)

# --- App Title ---
st.title("Agentic Ticket System")
#st.markdown("A simple interface to interact with our intelligent agent.")

# --- Initialize Session State for Messages ---
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Willkommen! Bitte beschreiben Sie Ihr Problem, damit ich ein Ticket für Sie erstellen kann."}]

# --- Display Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Chat Input and Sending Logic ---
if prompt := st.chat_input("Schreiben Sie Ihre Nachricht hier..."):
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- Send User Input to Backend (FastAPI) and Handle Streaming Response Directly in Assistant Bubble ---
    try:
        backend_url = "http://localhost:8000/chat"
        payload = {"message": prompt, "thread_id": get_thread_id()}
        with st.chat_message("assistant"):
            bot_response_placeholder = st.empty()
            full_response = ""
            with requests.post(backend_url, json=payload, stream=True) as response:
                response.raise_for_status()
                for chunk in response.iter_content(decode_unicode=True):
                    full_response += chunk
                    bot_response_placeholder.markdown(full_response)

            st.session_state.messages.append({"role": "assistant", "content": full_response})

    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with the backend: {e}")
        st.error(f"Details: {e}")