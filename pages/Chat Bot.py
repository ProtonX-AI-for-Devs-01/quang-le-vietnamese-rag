import streamlit as st
import requests
# Set up the Streamlit interface

# Load your logo image file
logo = "http://localhost:3001/_next/image?url=https%3A%2F%2Fstorage.googleapis.com%2Fprotonx-cloud-storage%2Fcropped-cropped-ProtonX-logo-1-1-300x100.png&w=256&q=75"

# Display the logo in the sidebar
st.sidebar.image(logo, width=100)

page = st.title("Chat with Ngrok")

def clear_session_state():
    for key in st.session_state.keys():
        del st.session_state[key]


import uuid  # Import the uuid module to generate unique IDs

# Generate a random session ID
session_id = str(uuid.uuid4())  # Creates a random UUID and converts it to a string

# Initialize the session state for the backend URL
if "flask_api_url" not in st.session_state:
    print('-go 1')
    st.session_state.flask_api_url = None

# Function to display the dialog and set the URL
@st.dialog("Setup Back end")
def vote():
    clear_session_state()
    st.markdown(
        """
        Run the backend [here](https://colab.research.google.com/drive/1XIZikuY3KtZzfnDG3wEcBBIHJhhdKgU-?usp=sharing) and paste the Ngrok link below.
        """
    )
    link = st.text_input("Backend URL", "")
    if st.button("Save"):
        st.session_state.flask_api_url = "{}/chat".format(link)  # Update ngrok URL
        st.rerun()  # Re-run the app to close the dialog


# Display the dialog only if the URL is not set
if st.session_state.flask_api_url is None:
    print('-go 2')
    vote()

# Once the URL is set, display it or proceed with other functionality
if "flask_api_url" in st.session_state:
    st.write(f"Backend is set to: {st.session_state.flask_api_url}")
    # Continue with the rest of your application logic


# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# URL of the Flask API

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



   