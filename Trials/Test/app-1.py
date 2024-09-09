from flask import Flask, render_template, redirect, request, flash, url_for, Response, jsonify,session
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import cv2
import base64
from psycopg2 import OperationalError 
from deepface import DeepFace
import numpy as np
from datetime import timedelta
from utils.camera_utils import generate_frames
from utils.db_utils import create_connection
from utils.emotion_analysis import predict_emotion, dynamic_weighted_average_emotion,analyze_image_emotion,analyze_text_emotion,save_emotion_data
from utils.auth_utils import register_user, login_user,forgot_pwd,verify,reset_pwd
from utils.profile_utils import fetch_data

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

app.permanent_session_lifetime = timedelta(days=3)

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

@app.route('/forgot_password', methods=["GET", "POST"])
def forgot_password():
    return forgot_pwd()

@app.route('/verify_otp', methods=["GET", "POST"])
def verify_otp():
    return verify()

@app.route('/reset_password', methods=["GET", "POST"])
def reset_password():
    return reset_pwd()

@app.route("/emotion", methods=["GET", "POST"])
def emotion():
    if 'user_id' in session:
        user_id = session['user_id']  
        if request.method == 'POST':
            image_data = request.form['image']
            text_input = request.form['text_input']  
            
            image_data_new= image_data.split(",")[1]  # Remove base64 header
            image_bytes = base64.b64decode(image_data_new)
            # Analyze the image and text emotions
            face_emotion, face_confidence = analyze_image_emotion(image_data)
            text_emotion, text_confidence = analyze_text_emotion(text_input, predict_emotion)
            
            # Get the final weighted emotion using dynamic weighted average
            final_emotion = dynamic_weighted_average_emotion(face_emotion, text_emotion, face_confidence, text_confidence)
            save_emotion_data(user_id, image_bytes,text_input, face_emotion, text_emotion, final_emotion)
            # Pass the final emotion, text emotion, and face emotion to the template
            return render_template('emotional_analysis.html', 
                                   final_emotion=final_emotion,
                                   text_emotion=text_emotion,
                                   face_emotion=face_emotion,
                                   user=user_id)  # Pass user_id for displaying it in the template
        
        # For GET requests, render the template without analysis results
        return render_template('emotional_analysis.html', 
                               final_emotion=None,
                               text_emotion=None,
                               face_emotion=None,
                               user=user_id)
    else:
        flash('Please log in first', 'warning')
        return redirect(url_for('login'))




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

@app.route("/feedback")
def feedback():
    return render_template("feedback.html")


if __name__ == '__main__':
    app.run(debug=True)
