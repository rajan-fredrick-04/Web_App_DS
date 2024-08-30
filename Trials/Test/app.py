import base64
from flask import Flask,render_template,redirect,request,flash,url_for,Response,jsonify
import psycopg2
from psycopg2 import OperationalError 
from werkzeug.security import generate_password_hash,check_password_hash
from dotenv import load_dotenv
import os
import cv2
from deepface import DeepFace
import time
from collections import Counter
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np


load_dotenv()

# Create a new Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

camera = cv2.VideoCapture(0)
if not camera.isOpened():
    raise IOError("Cannot open webcam")

# Load the face cascade
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def create_connection():
    try:
        conn=psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PWD"),
            port=os.getenv("DB_PORT")
            )
        cursor=conn.cursor();
        print("Connection to PostgreSQL DB successful")
        return conn, cursor
    except OperationalError as e:
        print(f"The error '{e}' occurred")
        return None, None



@app.route("/register",methods=['GET','POST'])
def register():
    if request.method=="POST":
        username=request.form['username']
        email=request.form['email']
        password=generate_password_hash(
            request.form['password'],
            method='pbkdf2:sha256',
            salt_length=8
            )
        connection,cursor=create_connection()
        try:
            if connection and cursor:
                cursor.execute('''INSERT INTO public."User_log" (username,password,email)VALUES (%s,%s,%s)''',
                                (username,password,email))
                connection.commit()
                flash('Registered successfully! Please log in.', 'success')
                return render_template("redirect.html", redirect_url=url_for('login'))
        except OperationalError as e:
            flash('Technical error occurred. Please try again later.', 'danger')
            print(f"Database error: {e}")
            return render_template("redirect.html", redirect_url=url_for('register'))
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
    return render_template("signup.html")

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']
        connection,cursor=create_connection()
        try:
            if connection and cursor:
                cursor.execute('''SELECT password FROM public."User_log" WHERE email = %s''', (email,))
                result = cursor.fetchone()
                if result is None:
                    flash('Invalid email or password', 'danger')
                    return redirect(url_for("login"))
                else:
                    stored_password = result[0]
                    if check_password_hash(stored_password, password):
                        # Password is correct, log the user in
                        return redirect(url_for("content"))  # Redirect to a home or dashboard page
                    else:
                        flash('Invalid email or password', 'danger')
        except OperationalError as e:
            flash('Technical error occurred. Please try again later.', 'danger')
            print(f"Database error: {e}")
        finally:
            cursor.close()
            connection.close()

    return render_template('login.html')

@app.route("/content")
def content():
    return render_template('contents.html')




def generate_frames():
    global current_emotion
    emotions = []  
    start_time = time.time()

    while True:
        # Read the camera frame
        success, frame = camera.read()
        if not success:
            break
        
        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = faceCascade.detectMultiScale(gray, 1.1, 4)
        
        # Analyze the frame using DeepFace
        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        
        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Collect the dominant emotion
        if 'dominant_emotion' in result[0]:
            dominant_emotion = result[0]['dominant_emotion']
            current_emotion = dominant_emotion 
            emotions.append(dominant_emotion)
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, dominant_emotion, (50, 50), font, 3, (0, 0, 255), 2, cv2.LINE_AA)
        
        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        # Exit after 20 seconds 
        if (time.time() - start_time) > 20:
            camera.release()
            break


@app.route('/get_emotion')
def get_emotion():
    return jsonify({'emotion': current_emotion})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

tokenizer = AutoTokenizer.from_pretrained("j-hartmann/emotion-english-distilroberta-base")
model = AutoModelForSequenceClassification.from_pretrained("j-hartmann/emotion-english-distilroberta-base")

def predict_emotion(text):
    # Tokenize the input text
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    # Get the model outputs
    outputs = model(**inputs)
    # Apply softmax to get probabilities
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    # Get the predicted label
    predicted_label = torch.argmax(probabilities, dim=1).item()
    # Map label to emotion
    label_map = {0: 'anger', 1: 'disgust', 2: 'fear', 3: 'joy', 4: 'neutral', 5: 'sadness', 6: 'surprise'}
    return label_map[predicted_label]

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    text = data['text']
    emotion = predict_emotion(text)
    return jsonify({'emotion': emotion})

@app.route("/emotion",methods=["GET","POST"])
def emotion():
    if request.method == 'POST':
        image_data = request.form['image']
        
        # Decode the image from base64
        image_data = image_data.split(',')[1]  # Remove the base64 header
        image_data = base64.b64decode(image_data)
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Analyze the image
        result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
        dominant_emotion = result[0]['dominant_emotion'] if 'dominant_emotion' in result[0] else 'No emotion detected'
        
        return render_template('emotional_analysis.html', emotion=dominant_emotion)
    
    return render_template('emotional_analysis.html', emotion=None)

if __name__=='__main__':
    app.run(debug=True)
        




