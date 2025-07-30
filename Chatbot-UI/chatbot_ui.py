import streamlit as st
import requests
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Changi Airport Assistant",
    page_icon="✈️",
    layout="centered"
)

# --- App Title and Description ---
st.title("Changi Airport AI Assistant ✈️")
st.write(
    "Welcome! I am your AI-powered assistant for Singapore Changi Airport. "
    "I can answer questions based on the content of the official website. "
    "Ask me about flights, dining, shopping, or amenities!"
)

# --- Configuration --
# Get the FastAPI backend URL from environment variable
FASTAPI_URL = os.getenv("FASTAPI_URL")

if not FASTAPI_URL:
    st.error("FASTAPI_URL is not set. Please check your environment variables.")

# --- Session State Initialization ---
# This is crucial for maintaining the conversation history.
# 'st.session_state' is a dictionary-like object that persists across reruns.
if "messages" not in st.session_state:
    # Start with a welcome message from the assistant
    st.session_state.messages = [
        {"role": "assistant", "content": "How can I help you today?"}
    ]

# --- Display Chat History ---
# Loop through the messages stored in the session state and display them
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Handle User Input ---
# st.chat_input displays a text input widget at the bottom of the page
if prompt := st.chat_input("What would you like to know?"):
    
    # 1. Add user's message to the session state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Get the assistant's response
    with st.chat_message("assistant"):
        # Use a spinner to indicate that the bot is "thinking"
        with st.spinner("Thinking..."):
            try:
                # Prepare the data for the POST request
                payload = {"question": prompt}
                
                # Make the API call to your FastAPI backend
                response = requests.post(FASTAPI_URL, json=payload)
                
                # Check for a successful response
                if response.status_code == 200:
                    response_data = response.json()
                    full_response = response_data.get("answer", "I'm sorry, I couldn't get a response.")
                else:
                    # Handle API errors (e.g., 500 Internal Server Error)
                    error_details = response.text
                    full_response = f"Sorry, I encountered an error. Status code: {response.status_code}\nDetails: {error_details}"
                    st.error(full_response)

            except requests.exceptions.RequestException as e:
                # Handle connection errors (e.g., the backend is not running)
                full_response = f"Could not connect to the chatbot API. Please make sure the backend server is running. Error: {e}"
                st.error(full_response)
        
        # Display the assistant's final response
        st.markdown(full_response)

    # 3. Add the assistant's response to the session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})