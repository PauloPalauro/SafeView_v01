from flask import Flask, Response, render_template
import cv2
from ultralytics import YOLO
import cvzone
import math
import time

app = Flask(__name__)

# Load YOLO model
model = YOLO("/home/ideal_pad/Documentos/SafeView_v01/BackEnd/YOLO-Weights/ppe.pt")
classNames = ['Capacete', 'Máscara', 'SEM-Capacete', 'SEM-Máscara', 'SEM-Colete', 'Pessoa', 'Colete']

def generate_frames():
    cap = cv2.VideoCapture(0)  # Initialize video capture with the default webcam
    cap.set(3, 1280)  # Set width
    cap.set(4, 720)   # Set height
    
    while True:
        # Capture frame-by-frame
        success, img = cap.read()
        if not success:
            break
        
        # Run YOLO model on the captured frame
        results = model(img, stream=True)
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Bounding Box
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                w, h = x2 - x1, y2 - y1

                # Confidence
                conf = math.ceil((box.conf[0] * 100)) / 100
                # Class Name
                cls = int(box.cls[0])
                currentClass = classNames[cls]
                
                # Set bounding box and text colors
                if conf > 0.5:
                    if currentClass in ['SEM-Capacete', 'SEM-Colete', 'SEM-Máscara']:
                        myColor = (0, 0, 255)  # Red
                    elif currentClass in ['Capacete', 'Colete', 'Máscara']:
                        myColor = (0, 255, 0)  # Green
                    else:
                        myColor = (255, 0, 0)  # Blue

                    # Draw bounding box and label
                    cvzone.putTextRect(img, f'{classNames[cls]} {conf}',
                                       (max(0, x1), max(35, y1)), scale=2, thickness=2,
                                       colorB=myColor, colorT=(255, 255, 255), colorR=myColor, offset=6)
                    cv2.rectangle(img, (x1, y1), (x2, y2), myColor, 3)

        # Convert the frame to JPEG format
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()

        # Use generator to output frames
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
