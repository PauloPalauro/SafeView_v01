from ultralytics import YOLO
import cv2
import cvzone
import math


def ppe_detection(): 
    cap = cv2.VideoCapture(0)  
    cap.set(3, 1280)  
    cap.set(4, 720)   

    model = YOLO("/home/ideal_pad/Documentos/SafeView_v01/BackEnd/YOLO-Weights/ppe.pt")

    classNames = ['Capacete', 'Mascara', 'SEM-Capacete', 'SEM-Mascara', 'SEM-Colete', 'Pessoa', 
                  'Colete']
    
    while True:
        success, img = cap.read()
        if not success:
            print("Failed to capture image from webcam.")
            break
        
        
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
                print(f"Class index: {cls}")

                if cls < len(classNames):
                    currentClass = classNames[cls]
                else:
                    currentClass = "Unknown"
                
                print(currentClass)
                
                if conf > 0.5:
                    if currentClass in ['SEM-Capacete', 'SEM-Colete', 'SEM-Mascara']:
                        myColor = (0, 0, 255)  # Red
                    elif currentClass in ['Capacete', 'Colete', 'Máscara']:
                        myColor = (0, 255, 0)  # Green
                    else:
                        myColor = (255, 0, 0)  # Blue

                    cvzone.putTextRect(img, f'{currentClass} {conf}',
                                       (max(0, x1), max(35, y1)), scale=2, thickness=2,
                                       colorB=myColor, colorT=(255, 255, 255), colorR=myColor, offset=6)
                    cv2.rectangle(img, (x1, y1), (x2, y2), myColor, 3)

        cv2.imshow("Image", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    ppe_detection()
