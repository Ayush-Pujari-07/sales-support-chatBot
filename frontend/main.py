# --------------------------------------- Sreamlit with Cookies --------------------------------------->
# streamlit_login.py
import requests
import streamlit as st

from http.cookies import SimpleCookie  # type: ignore

# FastAPI endpoints
REGISTER_URL = "http://127.0.0.1:9000/users"
LOGIN_URL = "http://127.0.0.1:9000/users/tokens"
CHAT_START_URL = "http://127.0.0.1:9000/chat/start"
ADD_MESSAGE_URL = "http://127.0.0.1:9000/chat"
ALL_CHAT_URL = "http://127.0.0.1:9000/allChat"


def set_cookie_in_header(refresh_token):
    cookies = SimpleCookie()
    cookies["refreshToken"] = refresh_token
    cookie_header = cookies.output(header="", sep=";").strip()
    return {"Cookie": cookie_header}


def register_user(email, password):
    return requests.post(REGISTER_URL, json={"email": email, "password": password})


def login_user(email, password):
    return requests.post(LOGIN_URL, json={"email": email, "password": password})


def start_chat(refresh_token):
    headers = set_cookie_in_header(refresh_token)
    return requests.post(CHAT_START_URL, headers=headers)


def add_message_to_chat(refresh_token, message, is_image=False, image_data=None):
    headers = set_cookie_in_header(refresh_token)
    data = {"message": message, "is_image": is_image}
    if is_image:
        data["image_data"] = image_data
    return requests.post(ADD_MESSAGE_URL, headers=headers, json=data)


def get_all_chat(refresh_token):
    headers = set_cookie_in_header(refresh_token)
    return requests.get(ALL_CHAT_URL, headers=headers)


st.title("Login Page")

# Registration form
st.subheader("Register")
register_email = st.text_input("Register Email")
register_password = st.text_input("Register Password", type="password")
if st.button("Register"):
    register_response = register_user(register_email, register_password)
    if register_response.status_code == 201:
        st.success("User registered successfully!")
    else:
        st.error("Registration failed!")

# Login form
st.subheader("Login")
login_email = st.text_input("Login Email")
login_password = st.text_input("Login Password", type="password")
if st.button("Login"):
    login_response = login_user(login_email, login_password)
    if login_response.status_code == 200:
        st.success("Logged in successfully!")
        tokens = login_response.json()
        st.session_state.refresh_token = tokens["refresh_token"]
        st.write("Access Token:", tokens["access_token"])
        st.write("Refresh Token:", tokens["refresh_token"])
    else:
        st.error("Login failed!")

# Chat section
if "refresh_token" in st.session_state:
    st.subheader("Chat")

    # Start chat
    if st.button("Start Chat"):
        start_chat_response = start_chat(st.session_state.refresh_token)
        if start_chat_response.status_code == 200:
            st.success("Chat started successfully!")
        else:
            st.error("Failed to start chat!")

    # Add message to chat
    chat_message = st.text_input("Message")
    if st.button("Send Message"):
        add_message_response = add_message_to_chat(st.session_state.refresh_token, chat_message)
        if add_message_response.status_code == 200:
            st.success("Message sent successfully!")
        else:
            st.error("Failed to send message!")

    # Get all chat messages
    if st.button("Get All Messages"):
        get_all_chat_response = get_all_chat(st.session_state.refresh_token)
        if get_all_chat_response.status_code == 200:
            chat_messages = get_all_chat_response.json()
            st.write("Chat Messages:", chat_messages)
        else:
            st.error("Failed to retrieve chat messages!")
