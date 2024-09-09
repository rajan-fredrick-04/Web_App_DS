import cv2
import numpy as np
import base64
from deepface import DeepFace
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import psycopg2
from utils.db_utils import create_connection
tokenizer = AutoTokenizer.from_pretrained("j-hartmann/emotion-english-distilroberta-base")
model = AutoModelForSequenceClassification.from_pretrained("j-hartmann/emotion-english-distilroberta-base")

def predict_emotion(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    outputs = model(**inputs)
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    predicted_label = torch.argmax(probabilities, dim=1).item()

    label_map = {0: 'anger', 1: 'disgust', 2: 'fear', 3: 'happy', 4: 'neutral', 5: 'sadness', 6: 'surprise'}
    return label_map[predicted_label]

def dynamic_weighted_average_emotion(face_emotion, text_emotion, face_confidence, text_confidence, text_preference_factor=1.5):
    # Assign numerical scores to emotions
    emotion_scores = {
        "anger": 0,
        "disgust": 1,
        "fear": 2,
        "sadness": 3,
        "neutral": 4,
        "surprise": 5,
        "happy": 6
    }

    face_score = emotion_scores.get(face_emotion, 2)
    text_score = emotion_scores.get(text_emotion, 2)

    adjusted_text_confidence = text_confidence * text_preference_factor

    total_confidence = face_confidence + adjusted_text_confidence
    face_weight = face_confidence / total_confidence
    text_weight = adjusted_text_confidence / total_confidence

    weighted_average = (face_weight * face_score) + (text_weight * text_score)
    
    score_to_emotion = {v: k for k, v in emotion_scores.items()}
    final_emotion = score_to_emotion.get(round(weighted_average), "neutral")
    
    return final_emotion

def analyze_image_emotion(image_data):
    # Decode the image from base64
    image_data = image_data.split(',')[1]  # Remove the base64 header
    image_data = base64.b64decode(image_data)
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Analyze the image for facial emotion
    face_result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
    face_emotion = face_result[0]['dominant_emotion'] if 'dominant_emotion' in face_result[0] else 'neutral'
    face_confidence = face_result[0]['emotion'][face_emotion] if face_emotion in face_result[0]['emotion'] else 1.0
    
    return face_emotion, face_confidence

def analyze_text_emotion(text_input, predict_emotion):
    # Analyze the text for emotion
    text_emotion = predict_emotion(text_input)
    text_confidence = 1.0  # Adjust if needed
    return text_emotion, text_confidence


def save_emotion_data(user_id, image_bytes,text_input, face_emotion, text_emotion, final_emotion):
    # SQL query to insert the data into the emotion_analysis table
    query = '''
        INSERT INTO public."input" (user_id, image, text, emotion, sentiment, aggregated_emotion)
        VALUES (%s, %s, %s, %s, %s, %s)
        '''
        
    
    # Establish a connection to the database
    conn,cursor=create_connection()
    
    try:
        # Execute the insert query with the provided data
        cursor.execute(query, (user_id, psycopg2.Binary(image_bytes), text_input, face_emotion, text_emotion, final_emotion))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error occurred while saving emotion data: {e}")
    finally:
       
        cursor.close()
        conn.close()