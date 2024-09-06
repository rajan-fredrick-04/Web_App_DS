import cv2
from deepface import DeepFace
import time

faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def generate_frames(camera):
    emotions = []  
    start_time = time.time()
    current_emotion = None

    while True:
        success, frame = camera.read()
        if not success:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.1, 4)

        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if 'dominant_emotion' in result[0]:
            dominant_emotion = result[0]['dominant_emotion']
            current_emotion = dominant_emotion
            emotions.append(dominant_emotion)

            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, dominant_emotion, (50, 50), font, 3, (0, 0, 255), 2, cv2.LINE_AA)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        if (time.time() - start_time) > 20:
            camera.release()
            break
