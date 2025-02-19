from flask import Flask, render_template, request, redirect, url_for
import cv2
import face_recognition
import os
import numpy as np
import io
import base64
import mysql.connector
import secrets
import requests

app = Flask(__name__)


# Connect to the database
mydb = mysql.connector.connect(
  host="ainlife.mysql.pythonanywhere-services.com",
  user="ainlife",
  password="Hamoda2799",
  database="ainlife$data"
)

# Create a table to store user data
mycursor = mydb.cursor()
# Check if the users table already exists
mycursor.execute("SHOW TABLES LIKE 'users'")
table_exists = mycursor.fetchone()

# Load known faces and names
known_faces = []
known_names = []

training_images_dir = "/home/ainlife/mysite/Training_images"
for filename in os.listdir(training_images_dir):
    # Load image
    image = face_recognition.load_image_file(f"{training_images_dir}/{filename}")
    # Get face encoding
    face_encoding = face_recognition.face_encodings(image)[0]
    # Add to known faces and names
    known_faces.append(face_encoding)
    known_names.append(filename.split(".")[0])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

# Define a global variable to store the signup data
signup_data = []

...

@app.route("/signup", methods=["POST"])
def signup_post():
    # Get user name and email from form
    full_name = request.form.get("name")
    user_name = request.form.get("user")
    user_email = request.form.get("email")
    password1 = request.form.get("pass1")
    password2 = request.form.get("pass2")
    number = request.form.get("phone")
    address1 = request.form.get("adress")
    brd = request.form.get("birth")
    bloodgroup = request.form.get("blood")
    gender = request.form.get("sex")











    if user_name is None or user_name == "":
        return "Username is required"
    if user_email is None or user_email == "":
        return "Email is required"
    if password1 is None or password1 == "":
        return "Password is required"
    if password2 is None or password2 == "":
        return "Confirm password is required"
    if password1 != password2:
        return "Passwords do not match"
    if number is None or number == "":
        return "Phone number is required"
    if address1 is None or address1 == "":
        return "Address is required"
    if brd is None or brd == "":
        return "Birthdate is required"
    if bloodgroup is None or bloodgroup == "":
        return "Blood group is required"
    if gender is None or gender == "":
        return "Gender is required"
    #mycursor = mydb.cursor()
    #sql = "INSERT INTO users (username, token, email) VALUES (%s, %s, %s)"
    #val = (user_name, user_email)
    #mycursor.execute(sql, val)
    #mydb.commit()

    # Convert the base64-encoded video stream from the browser to an OpenCV frame
    video_stream = request.form.get("video_stream")
    video_bytes = io.BytesIO(base64.b64decode(video_stream.split(',')[1]))
    video_np = np.frombuffer(video_bytes.getvalue(), dtype=np.uint8)
    frame = cv2.imdecode(video_np, 1)

    # Convert frame to RGB
    rgb_frame = frame[:, :, ::-1]

    # Get face locations and encodings
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    if len(face_encodings) == 0:
        return "No face detected, please try again"

    # Save image file
    face_encoding = face_encodings[0]
    image_path = f"{training_images_dir}/{user_name}.jpg"
    cv2.imwrite(image_path, frame)



    # Update known_faces and known_names lists
    known_faces.append(face_encoding)
    known_names.append(user_name)

    redirect_url = "https://health.aiiot.website/api/new_reg.php/"+"?name="+full_name +"&user=" + user_name + "&email=" + user_email + "&pass1=" + password1 + "&pass2="  + password2 + "&phone=" + number + "&adress=" + address1 + "&birth=" + brd + "&blood=" + bloodgroup + "&sex=" + gender
    response = requests.get(redirect_url)


    return redirect(url_for('index'))
    #return redirect(url_for(redirect_url))


@app.route("/login", methods=["POST"])
def login():
    # Convert the base64-encoded video stream from the browser to an OpenCV frame
    video_stream = request.form.get("video_stream")
    video_bytes = io.BytesIO(base64.b64decode(video_stream.split(',')[1]))
    video_np = np.frombuffer(video_bytes.getvalue(), dtype=np.uint8)
    frame = cv2.imdecode(video_np, 1)

    # Convert frame to RGB
    rgb_frame = frame[:, :, ::-1]

    # Get face locations and encodings
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # Check if face encoding matches with known face encoding
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_faces, face_encoding)
        face_distances = face_recognition.face_distance(known_faces, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            # Generate a token for the user

            user_name = known_names[best_match_index]
            # Store the token in the database




            return redirect("https://health.aiiot.website/api/face_login.php/?user="+user_name)

    return "Face not recognized, please try again"



@app.route("/home/<username>")
def home(username):
    # Redirect to the dashboard URL
    return redirect("https://health.aiiot.website/dashboard/patient/template.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)