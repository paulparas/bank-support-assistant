import uuid
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import requests

header_html = """
<div style="background-color: #4CAF50; padding: 20px; border-radius: 5px;">
    <h1 style="color: white; text-align: center;">My Custom Header</h1>
</div>
"""

def handle_send_button():
    st.session_state.send_button_click = False  # Reset the flag
    user_message = st.session_state.widget
    if user_message.strip():
        st.session_state.user_message = user_message
        st.session_state.widget = ""
        conversation_id = st.session_state.conversationId
        # Send the message to the Flask application
        response = requests.post(f'http://localhost:5000/conversation/{conversation_id}', json={'message': user_message})

        # Check if the response is valid
        if response.status_code == 200:
            bot_response = response.text

            # Append the conversation to the session state
            st.session_state.messages.append({
                'user_message': user_message,
                'bot_response': bot_response
            })
            # st.session_state.message = ""

            # Clear the input box after sending
            # st.session_state.user_message = ""  # Clear the input box
            # st.rerun()  # Refresh the page to show the updated conversation history
        else:
            st.error("Error communicating with the assistant. Please try again.")
    # 
        

# st.markdown(header_html, unsafe_allow_html=True)
# Set page configuration
st.set_page_config(layout="wide")
st.markdown('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">', unsafe_allow_html=True)
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"/>',
    unsafe_allow_html=True,
)
# Custom CSS for chatbot UI and page background
st.markdown("""
<nav class="navbar fixed-top navbar-expand-lg navbar-dark" style="background-color: #2e7d32; padding:0">
    <div class="container-fluid d-flex justify-content-center">
        <h2 style="color: white; text-align: center;">Virtual Assistant</h2>
    </div>
</nav>
<style>
        #MainMenu {visibility: hidden;}
        [data-testid="stHeader"] {
                display: none;
        }
        body {
                background-color: white;
        }
        .user-message {
                background-color: #2e7d32;
                border-radius: 8px;
                padding: 8px;
                margin: 10px 0;
                text-align: right;
                color: #FFFFFF;
                justify-self: flex-end;
                width: fit-content;
        }
        .bot-message {
                background-color: #F1F0F0;
                border-radius: 8px;
                padding: 8px;
                margin: 10px 0;
                text-align: left;
                justify-self: flex-start; 
                width: fit-content;
        }
        .message-container {
                display: flex;
                flex-direction: column;
        }
        .message-container .user-message {
                align-self: flex-end;
        }
        .message-container .bot-message {
                align-self: flex-start;
        }
</style>
""", unsafe_allow_html=True)

# Title with emojis to make it more visually appealing
# st.title("💼 Banking Virtual Assistant 💬")

# Initialize the session state to store the conversation history and conversationId
if 'conversationId' not in st.session_state:
    st.session_state.conversationId = str(uuid.uuid4())
    
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display conversation history
st.markdown('<div class="message-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    st.markdown(f'<div class="user-message">{msg["user_message"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bot-message">{msg["bot_response"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Input text box for user message
user_message = st.text_input("", key="widget", placeholder="Enter your message...", on_change=handle_send_button)

with stylable_container(
    key="container_with_border",
    css_styles=r"""
        button p:before {
            font-family: 'Font Awesome 5 Free';
            content: '\f1d8';
            display: inline-block;
            padding-right: 3px;
            vertical-align: middle;
            font-weight: 900;
        }
        """,
):
# Send button
    send_button = st.button("Send")
if send_button or st.session_state.get('send_button_click', False):
    handle_send_button()
# Ensure the input box and send button are fixed at the bottom of the page
st.markdown("""
<style>
    .stTextInput, .stButton {
        position: fixed;
        bottom: 10px;
        width: 85%;
        left: 5%;
        display: inline-block;
    }
    .stButton {
        width: 5%;
        left: 91%;
    }
</style>
""", unsafe_allow_html=True)



# handle_send_button()
