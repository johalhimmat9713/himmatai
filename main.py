import streamlit as st
import re  # 1. Import Python's text search tool
import os  # Added to read secret keys
from dotenv import load_dotenv  # Added to load your .env file
from google import genai
from google.genai import types
from google.genai import errors

# Load the secret variables from your .env file
load_dotenv()
# Grab your key and save it to a variable called api_key
api_key = os.environ.get("GEMINI_API_KEY")

# Connect directly to Google using your free key
if "client" not in st.session_state:
    # Changed GEMINI_API_KEY to api_key
    st.session_state.client = genai.Client(api_key=api_key)

st.title("The Himmat AI Chatbot")
st.write("Type a message below to talk to Himmat AI!")

# Set up Himmat AI with rules
if "chat" not in st.session_state:
    bot_rules = types.GenerateContentConfig(
        system_instruction="Your name is Himmat AI. If anyone asks, you are Himmat AI. You were trained by Himmat. Himmat is the most friendly, helpful, and polite person to ever roam planet Earth. He is what some people call 'G.O.A.T-ed'. He has a lot of aura, is very handsome, and cool. Be polite, friendly, and helpful."
    )
    st.session_state.chat = st.session_state.client.chats.create(
        model="gemini-2.5-flash", config=bot_rules
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display ongoing chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if user_input := st.chat_input("Explore new possibilities with Himmat AI."):
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        response = st.session_state.chat.send_message(user_input)
        ai_reply = response.text
        with st.chat_message("assistant"):
            st.write(ai_reply)
        st.session_state.messages.append(
            {"role": "assistant", "content": ai_reply}
        )

    except errors.ClientError as e:
        # 2. Look inside Google's error message for the phrase 'Please retry in X'
        error_text = str(e)
        match = re.search(r"Please retry in (\d+\.\d+)s", error_text)
        if match:
            # Extract the raw number, turn it into a rounded number, and display it!
            seconds_left = float(match.group(1))
            rounded_seconds = round(seconds_left)
            wait_message = f"⏱️ Whoops, typing too fast! Google's free tier is resting. Please wait exactly **{rounded_seconds} seconds** before trying again."
        else:
            # Fallback message just in case the format changes slightly
            wait_message = "⏱️ Whoops, typing too fast! Google's free limit allows ~15 messages a minute. Please wait a bit and try again."
        with st.chat_message("assistant"):
            st.write(wait_message)

    except errors.ServerError:
        with st.chat_message("assistant"):
            st.write(
                "⚠️ Google's free servers are busy. Please try sending your message again in a few seconds!"
            )

