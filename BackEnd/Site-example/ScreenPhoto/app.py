import asyncio
from typing import List
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, Response, JSONResponse, StreamingResponse
from pydantic import BaseModel
import cv2
import numpy as np
from ultralytics import YOLO
import cvzone
import math
import base64
import time
import os

app = FastAPI()

# Carregar os modelos YOLO
model = YOLO("../../YOLO-Weights/ppe.pt")
model_person = YOLO("yolov8n.pt")
model_person.classes = [0]

classNames = ['Capacete', 'Máscara', 'SEM-Capacete', 'SEM-Máscara', 'SEM-Colete', 'Pessoa', 'Colete']

def draw_box(img, box, class_name, conf, color):
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
    cvzone.putTextRect(img, f'{class_name} {conf:.2f}', (max(0, x1), max(35, y1)), scale=2, thickness=2, colorB=color, colorT=(255, 255, 255), offset=6)

def analyze_image(img, save_path=None):
    all_ok = True
    results = model(img, stream=True)
    
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            conf = box.conf[0]
            if cls < len(classNames) and conf > 0.5:
                class_name = classNames[cls]
                color = (0, 0, 255) if "SEM" in class_name else (0, 255, 0)
                draw_box(img, box, class_name, conf, color)
                if "SEM" in class_name:
                    all_ok = False

    # Salvar a imagem se o caminho for fornecido
    if save_path:
        cv2.imwrite(save_path, img)
        print(f"Imagem salva em: {save_path}")
    
    return img, all_ok

async def generate_frames():
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    person_detected, detection_pause_time, photo_taken, analysis_paused = False, 0, False, False
    pause_printed = False  # Variável para controlar a exibição do print

    while True:
        success, img = cap.read()
        if not success:
            break

        current_time = time.time()

        # Controle de pausa para detecção de pessoa
        if not person_detected or (current_time - detection_pause_time > 10):
            if person_detected and not photo_taken:
                save_path = f"result_photo_{int(current_time)}.jpg"  # Caminho para salvar a imagem
                result_img, all_ok = analyze_image(img, save_path=save_path)  # Salva diretamente na função
                print("Analise volta em 10")
                photo_taken, analysis_paused, pause_printed = True, True, False  # Reset pause_printed
                pause_start_time = current_time

            # Verifica se o tempo de pausa acabou
            if not analysis_paused or (current_time - pause_start_time > 10):
                analysis_paused = False
                
                if not pause_printed:  # Mostra o print apenas uma vez quando a pausa acabar
                    print("Análise voltou")
                    pause_printed = True  # Garante que o print não será mostrado novamente até a próxima pausa

                results = model_person(img, stream=True, verbose=False, classes=[0])
                for r in results:
                    for box in r.boxes:
                        if int(box.cls[0]) == 0 and box.conf[0] > 0.5:
                            person_detected, detection_pause_time, photo_taken = True, current_time, False
                            print("Pessoa Detectada. Tirando foto em 10 segundos")
                            draw_box(img, box, "Pessoa", box.conf[0], (0, 255, 0))

        ret, buffer = cv2.imencode('.jpg', img)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    cap.release()

@app.get("/", response_class=FileResponse)
async def index():
    return FileResponse("index.html")

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
