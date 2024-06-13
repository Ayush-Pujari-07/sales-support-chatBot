import streamlit as st
import requests
import json

CHAT_START_URL = "http://127.0.0.1:9000/chat/start"
ADD_MESSAGE_URL = "http://127.0.0.1:9000/chat"
ALL_CHAT_URL = "http://127.0.0.1:9000/allChat"


def set_cookie_in_header(refresh_token):
    from http.cookies import SimpleCookie  # type: ignore
    cookies = SimpleCookie()
    cookies["refreshToken"] = refresh_token
    cookie_header = cookies.output(header="", sep=";").strip()
    return {"Cookie": cookie_header}


def start_chat(refresh_token):
    try:
        headers = set_cookie_in_header(refresh_token)
        response = requests.post(CHAT_START_URL, headers=headers)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        st.error(f"Start chat request failed: {e}")
        return None


def add_message_to_chat(refresh_token, message, is_image=False, image_data=None):
    try:
        headers = set_cookie_in_header(refresh_token)
        data = {"message": message, "is_image": is_image}
        if is_image:
            data["image_data"] = image_data
        response = requests.post(ADD_MESSAGE_URL, headers=headers, json=data)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        st.error(f"Add message request failed: {e}")
        return None


def get_all_chat(refresh_token):
    try:
        headers = set_cookie_in_header(refresh_token)
        response = requests.get(ALL_CHAT_URL, headers=headers)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        st.error(f"Get all chat request failed: {e}")
        return None


def display_chat_messages(messages):
    for message in messages:
        if message['role'] == 'user':
            st.markdown(f"**You:** {message['message']}")
        else:
            st.markdown(f"**Assistant:** {message['message']}")


def chat_page():
    st.title("Chat")

    if st.button("Start Chat"):
        start_chat_response = start_chat(st.session_state.refresh_token)
        if start_chat_response and start_chat_response.status_code == 200:
            st.success("Chat started successfully!")
        else:
            st.error("Failed to start chat!")

    chat_message = st.text_input("Message")
    if st.button("Send Message"):
        add_message_response = add_message_to_chat(st.session_state.refresh_token, chat_message)
        if add_message_response and add_message_response.status_code == 200:
            st.success("Message sent successfully!")
        else:
            st.error("Failed to send message!")

    if st.button("Get All Messages"):
        get_all_chat_response = get_all_chat(st.session_state.refresh_token)
        if get_all_chat_response and get_all_chat_response.status_code == 200:
            chat_messages = get_all_chat_response.json()
            display_chat_messages(chat_messages)
        else:
            st.error("Failed to retrieve chat messages!")

    # Automatically load chat messages when the page loads
    if 'refresh_token' in st.session_state:
        get_all_chat_response = get_all_chat(st.session_state.refresh_token)
        if get_all_chat_response and get_all_chat_response.status_code == 200:
            chat_messages = get_all_chat_response.json()
            display_chat_messages(chat_messages)
