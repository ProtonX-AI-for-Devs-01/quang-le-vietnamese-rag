import streamlit as st

logo = "http://localhost:3001/_next/image?url=https%3A%2F%2Fstorage.googleapis.com%2Fprotonx-cloud-storage%2Fcropped-cropped-ProtonX-logo-1-1-300x100.png&w=256&q=75"

# Display the logo in the sidebar
st.sidebar.image(logo, width=100)

st.title("Chat with Ngrok")


st.write("# Welcome to ProtonX AI App 👋")

st.markdown(
    """
        List Backend was listed here:
        - Chabot Backend: [Link Colab](https://colab.research.google.com/drive/1XIZikuY3KtZzfnDG3wEcBBIHJhhdKgU-?usp=sharing)

    """
)