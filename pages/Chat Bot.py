import streamlit as st
import requests
# Set up the Streamlit interface

# Load your logo image file
logo = "http://localhost:3001/_next/image?url=https%3A%2F%2Fstorage.googleapis.com%2Fprotonx-cloud-storage%2Fcropped-cropped-ProtonX-logo-1-1-300x100.png&w=256&q=75"

# Display the logo in the sidebar
st.sidebar.image(logo, width=100)

page = st.title("Flower shop chatbot")

def clear_session_state():
    for key in st.session_state.keys():
        del st.session_state[key]


import uuid  # Import the uuid module to generate unique IDs

# Generate a random session ID
session_id = str(uuid.uuid4())  # Creates a random UUID and converts it to a string

# URL of the Flask API
st.session_state.flask_api_url = "http://localhost:5000/api/v1/chat"

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# Display the chat history using chat UI
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    # Prepare the payload for the request
    with st.chat_message("assistant"):
        payload = {
            "query": prompt,
            "session_id": session_id
        }
        # Send the POST request to the Flask API
        response = requests.post(st.session_state.flask_api_url, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            # Get the response from the API
            api_response = response.json()
            # Add the assistant's response to the chat history
            st.markdown(api_response['content'])
            st.session_state.chat_history.append({"role": "assistant", "content": api_response['content']})
        else:
            st.error(f"Error: {response.status_code}")



   