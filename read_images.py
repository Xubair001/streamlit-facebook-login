import json
import os

from gridfs import GridFS
from pymongo import MongoClient

# MongoDB setup (replace with your MongoDB URI)
mongo_uri = "mongodb+srv://abdullahzubair356:kadharkadhar@facebook-login.6fv4m.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)

# Access the database and GridFS
db = client["user_db"]
fs = GridFS(db)


# Function to download images from GridFS and store usernames/passwords in a JSON file
def download_images_and_save_credentials():
    # Fetch all the image documents from the images collection
    image_documents = db.images.find()

    # Check if directory exists to save images, if not create it
    if not os.path.exists("downloaded_images"):
        os.makedirs("downloaded_images")

    # Initialize an empty list to store user credentials
    user_credentials = []

    # Fetch all user credentials from the 'users' collection
    users = db.users.find()

    # Loop through the users to store their credentials in a list of dictionaries
    for user in users:
        user_credentials.append(
            {"username": user["username"], "password": user["password"]}
        )

    # Write the list of dictionaries to a JSON file
    with open("user_credentials.json", "w") as json_file:
        json.dump(user_credentials, json_file, indent=4)

    print("User credentials saved in 'user_credentials.json'.")

    # Loop through the image documents to download images
    for image_doc in image_documents:
        # Retrieve image_id from the document
        image_id = image_doc.get("image_id")

        # Fetch the image binary data from GridFS using the image_id
        image_data = fs.get(image_id)

        # Create the image filename (you can customize this part)
        image_filename = f"downloaded_images/{image_doc['username']}_{image_id}.png"

        # Save the image as a .png file
        with open(image_filename, "wb") as f:
            f.write(image_data.read())  # Write the binary data to the file

        print(f"Image saved as: {image_filename}")


# Call the function to download and save images, and save user credentials
download_images_and_save_credentials()
