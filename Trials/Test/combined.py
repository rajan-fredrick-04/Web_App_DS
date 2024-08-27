from collections import Counter
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from deepface import DeepFace
import cv2
import time

# Initialize RoBERTa model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("j-hartmann/emotion-english-distilroberta-base")
model = AutoModelForSequenceClassification.from_pretrained("j-hartmann/emotion-english-distilroberta-base")

def predict_emotion(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    outputs = model(**inputs)
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    predicted_label = torch.argmax(probabilities, dim=1).item()
    label_map = {0: 'anger', 1: 'disgust', 2: 'fear', 3: 'joy', 4: 'neutral', 5: 'sadness', 6: 'surprise'}
    return label_map[predicted_label]

# Initialize the webcam and face detection
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Cannot open webcam")

faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

start_time = time.time()
emotions = []

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, 1.1, 4)
    result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
    
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    if 'dominant_emotion' in result[0]:
        dominant_emotion = result[0]['dominant_emotion']
        emotions.append(dominant_emotion)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, dominant_emotion, (50, 50), font, 3, (0, 0, 255), 2, cv2.LINE_AA)
    
    cv2.imshow("Original Video", frame)
    
    if cv2.waitKey(2) & 0xFF == ord('q') or (time.time() - start_time) > 15:
        break

cap.release()
cv2.destroyAllWindows()

# Get the most common emotion from facial detection
if emotions:
    face_emotion = Counter(emotions).most_common(1)[0][0]
else:
    face_emotion = "neutral"

# Assuming you have the text input
text_input = "Your text here for sentiment analysis."
text_emotion = predict_emotion(text_input)

# Combine the emotions (you can tweak this logic as needed)
combined_emotions = [face_emotion, text_emotion]
final_emotion = Counter(combined_emotions).most_common(1)[0][0]

print(f"Final detected emotion: {final_emotion}")import cv2
from deepface import DeepFace
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import time
from collections import Counter

# Mapping emotions to numerical values
emotion_scores = {
    'angry': 1,
    'disgust': 2,
    'fear': 3,
    'sad': 4,
    'neutral': 5,
    'surprise': 6,
    'happy': 7
}

# Camera setup
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    cap = cv2.VideoCapture(1)
if not cap.isOpened():
    raise IOError("Cannot open webcam")

# Load the face cascade
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Load the RoBERTa model
tokenizer = AutoTokenizer.from_pretrained("j-hartmann/emotion-english-distilroberta-base")
model = AutoModelForSequenceClassification.from_pretrained("j-hartmann/emotion-english-distilroberta-base")

def predict_emotion(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    outputs = model(**inputs)
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    predicted_label = torch.argmax(probabilities, dim=1).item()
    label_map = {0: 'angry', 1: 'disgust', 2: 'fear', 3: 'happy', 4: 'neutral', 5: 'sad', 6: 'surprise'}
    return label_map[predicted_label]

def get_most_common_emotion(emotions):
    if emotions:
        counter = Counter(emotions)
        return counter.most_common(1)[0][0]  # Get the most common emotion
    else:
        return None

def weighted_average_emotion(face_emotion, text_emotion, face_weight=0.6, text_weight=0.4):
    if face_emotion is None or text_emotion is None:
        return None
    
    face_emotion_score = emotion_scores.get(face_emotion, 0)
    text_emotion_score = emotion_scores.get(text_emotion, 0)
    
    weighted_score = (face_emotion_score * face_weight) + (text_emotion_score * text_weight)
    closest_emotion = min(emotion_scores, key=lambda k: abs(emotion_scores[k] - weighted_score))
    
    return closest_emotion

# Initialize variables
start_time = time.time()
emotions = []

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, 1.1, 4)
    
    result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
    
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    if 'dominant_emotion' in result[0]:
        dominant_emotion = result[0]['dominant_emotion']
        emotions.append(dominant_emotion)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, dominant_emotion, (50, 50), font, 3, (0, 0, 255), 2, cv2.LINE_AA)
    
    cv2.imshow("Original Video", frame)
    
    if cv2.waitKey(2) & 0xFF == ord('q') or (time.time() - start_time) > 15:
        break

cap.release()
cv2.destroyAllWindows()

# Process the text
text = input("Enter a sentence for emotion detection: ")
text_emotion = predict_emotion(text)
print(f"Detected emotion from text: {text_emotion}")

# Get the most common face emotion
most_common_emotion = get_most_common_emotion(emotions)
print(f"Most common face emotion: {most_common_emotion}")

# Calculate the final emotion using the weighted average method
final_emotion = weighted_average_emotion(most_common_emotion, text_emotion, face_weight=0.6, text_weight=0.4)
print(f"Final detected emotion based on weighted average: {final_emotion}")

