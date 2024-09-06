from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

tokenizer = AutoTokenizer.from_pretrained("j-hartmann/emotion-english-distilroberta-base")
model = AutoModelForSequenceClassification.from_pretrained("j-hartmann/emotion-english-distilroberta-base")

def predict_emotion(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    outputs = model(**inputs)
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    predicted_label = torch.argmax(probabilities, dim=1).item()

    label_map = {0: 'anger', 1: 'disgust', 2: 'fear', 3: 'joy', 4: 'neutral', 5: 'sadness', 6: 'surprise'}
    return label_map[predicted_label]

def dynamic_weighted_average_emotion(face_emotion, text_emotion, face_confidence, text_confidence, text_preference_factor=1.5):
    # Assign numerical scores to emotions
    emotion_scores = {
        "happy": 3,
        "neutral": 2,
        "sad": 1,
        "angry": 0
    }

    # Get the scores for the face and text emotions
    face_score = emotion_scores.get(face_emotion, 2)
    text_score = emotion_scores.get(text_emotion, 2)

    # Apply a preference factor to text confidence to give it more weight
    adjusted_text_confidence = text_confidence * text_preference_factor

    # Calculate total confidence (with adjusted text confidence)
    total_confidence = face_confidence + adjusted_text_confidence
    face_weight = face_confidence / total_confidence
    text_weight = adjusted_text_confidence / total_confidence

    # Compute the weighted average of the emotion scores
    weighted_average = (face_weight * face_score) + (text_weight * text_score)
    
    # Map the weighted average back to the closest emotion
    score_to_emotion = {v: k for k, v in emotion_scores.items()}
    final_emotion = score_to_emotion.get(round(weighted_average), "neutral")
    
    return final_emotion
