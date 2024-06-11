import streamlit as st
import requests

FASTAPI_URL = "http://localhost:8000"


def home_page():
    st.write("Welcome to the Home page!")


def profile_page():
    st.write("Welcome to the Profile page!")


def settings_page():
    st.write("Welcome to the Settings page!")


def login_page():
    st.write("Please log in to access the application.")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        response = requests.post(f"{FASTAPI_URL}/login", json={"username": username, "password": password})
        if response.status_code == 200:
            st.session_state['logged_in'] = True
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")


if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login_page()
else:
    menu_selection = st.sidebar.radio("Menu", ["Home", "Profile", "Settings", "Logout"])

    if menu_selection == "Home":
        home_page()
    elif menu_selection == "Profile":
        profile_page()
    elif menu_selection == "Settings":
        settings_page()
    elif menu_selection == "Logout":
        st.session_state['logged_in'] = False
        st.experimental_rerun()
