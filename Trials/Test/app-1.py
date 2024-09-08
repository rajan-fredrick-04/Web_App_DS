from flask import Flask, render_template, redirect, request, flash, url_for, Response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import cv2
import base64
from psycopg2 import OperationalError 
from deepface import DeepFace
import numpy as np
from utils.camera_utils import generate_frames
from utils.db_utils import create_connection
from utils.emotion_analysis import predict_emotion, dynamic_weighted_average_emotion
from utils.auth_utils import register_user, login_user
from utils.profile_utils import fetch_data

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

camera = cv2.VideoCapture(0)
if not camera.isOpened():
    raise IOError("Cannot open webcam")

# @app.route('/video')
# def video():
#     return Response(generate_frames(camera), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/register", methods=['GET', 'POST'])
def register():
    return register_user(request)  # Call the function from auth_utils.py

@app.route("/login", methods=['GET', 'POST'])
def login():
    return login_user(request) 


@app.route("/emotion", methods=["GET", "POST"])
def emotion():
    if request.method == 'POST':
        image_data = request.form['image']
        text_input = request.form['text_input']  # Get text input from the form
        
        # Decode the image from base64
        image_data = image_data.split(',')[1]  # Remove the base64 header
        image_data = base64.b64decode(image_data)
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Analyze the image for facial emotion
        face_result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
        face_emotion = face_result[0]['dominant_emotion'] if 'dominant_emotion' in face_result[0] else 'neutral'
        face_confidence = face_result[0]['emotion'][face_emotion] if face_emotion in face_result[0]['emotion'] else 1.0
        
        # Analyze the text for emotion
        text_emotion = predict_emotion(text_input)
        text_confidence = 1.0  # You can later adjust this based on the output from the text model
        
        # Get the final weighted emotion using dynamic weighted average
        final_emotion = dynamic_weighted_average_emotion(face_emotion, text_emotion, face_confidence, text_confidence)
        
        # Pass the final emotion, text emotion, and face emotion to the template
        return render_template('emotional_analysis.html', 
                               final_emotion=final_emotion,
                               text_emotion=text_emotion,
                               face_emotion=face_emotion)
    
    return render_template('emotional_analysis.html', 
                           final_emotion=None,
                           text_emotion=None,
                           face_emotion=None)



@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    text = data['text']
    emotion = predict_emotion(text)
    return jsonify({'emotion': emotion})


@app.route("/recommends")
def recommendation():
    return render_template('1_recommends_page.html')

@app.route("/profile-view")
def pofile_view():
    return fetch_data()
@app.route("/profile-edit",methods=["GET","POST"])
def profile_edit():
    if request.method=="POST":
        name=request.form["name"]
        dob=request.form["dob"]



if __name__ == '__main__':
    app.run(debug=True)
