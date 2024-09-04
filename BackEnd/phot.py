from ultralytics import YOLO
import cv2
import cvzone
import math
import time

def ppe_detection():
    # Initialize video capture with the default webcam
    cap = cv2.VideoCapture(0)  # For Webcam
    cap.set(3, 1280)  # Set width
    cap.set(4, 720)   # Set height

    # Load YOLO model
    model = YOLO("/home/ideal_pad/Documentos/SafeView_v01/BackEnd/YOLO-Weights/ppe.pt")

    # Class names for detection
    classNames = ['Capacete', 'Mascara', 'SEM-Capacete', 'SEM-Mascara', 'SEM-Colete', 'Pessoa', 'Colete']

    while True:
        # Show message on the screen for 3 seconds
        img = cv2.imread("/home/ideal_pad/Documentos/SafeView_v01/BackEnd/logo.png")  # Display a black screen or any image to show the message
        cv2.putText(img, "Tirando foto em 3 segundos...", (200, 360), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        cv2.imshow("Message", img)
        cv2.waitKey(1000)  # Show for 1 second
        time.sleep(2)  # Wait for remaining 2 seconds
        
        # Close the message window
        cv2.destroyWindow("Message")

        # Capture a single frame from the webcam
        success, img = cap.read()
        if not success:
            print("Failed to capture image from webcam.")
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
                print(currentClass)
                
                # Set bounding box and text colors
                if conf > 0.5:
                    if currentClass in ['SEM-Capacete', 'SEM-Colete', 'SEM-Mascara']:
                        myColor = (0, 0, 255)  # Red
                    elif currentClass in ['Capacete', 'Colete', 'Mascara']:
                        myColor = (0, 255, 0)  # Green
                    else:
                        myColor = (255, 0, 0)  # Blue

                    # Draw bounding box and label
                    cvzone.putTextRect(img, f'{classNames[cls]} {conf}',
                                       (max(0, x1), max(35, y1)), scale=2, thickness=2,
                                       colorB=myColor, colorT=(255, 255, 255), colorR=myColor, offset=6)
                    cv2.rectangle(img, (x1, y1), (x2, y2), myColor, 3)

        # Show the image with detections
        cv2.imshow("Image", img)

        # Wait for key press; if 'q' is pressed, exit loop
        if cv2.waitKey(0) & 0xFF == ord('q'):
            break

    # Release the capture and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    ppe_detection()