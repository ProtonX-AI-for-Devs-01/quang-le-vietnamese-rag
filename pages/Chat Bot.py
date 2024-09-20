import streamlit as st
import requests
# Set up the Streamlit interface

# # Load your logo image file
logo = "https://hoatuoimymy.com/wp-content/uploads/2024/08/logo-hoa-tuoi-my-my-fn-n.png"

# Display the logo in the sidebar
st.sidebar.image(logo, width=227)

page = st.title("Shop Hoa Tươi My My hân hạnh được phục vụ quí khách")

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
if prompt := st.chat_input("Bạn có cần tư vấn sản phẩm gì hôm nay không?"):
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



   