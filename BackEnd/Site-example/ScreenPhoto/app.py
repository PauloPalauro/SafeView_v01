import asyncio
from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, Response, JSONResponse, StreamingResponse
import cv2
import numpy as np
from ultralytics import YOLO
import cvzone
import math
import base64
import time
import os
import torch

app = FastAPI()

clients = []

# Carregar os modelos YOLO
model = YOLO("../../YOLO-Weights/ppe.pt")
model_person = YOLO("yolov8n.pt")
model_person.classes = [0]

last_analyzed_image_path = None

classNames = ['Capacete', 'Máscara', 'SEM-Capacete', 'SEM-Máscara', 'SEM-Colete', 'Pessoa', 'Colete']

def draw_box(img, box, class_name, conf, color):
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
    cvzone.putTextRect(img, f'{class_name} {conf:.2f}', (max(0, x1), max(35, y1)), scale=2, thickness=2, colorB=color, colorT=(255, 255, 255), offset=6)


async def send_message_to_clients(message, prefix):
    for client in clients:
        try:
            # Envia a mensagem com o prefixo especificado
            await client.send_text(f"{prefix}:{message}")
        except WebSocketDisconnect:
            clients.remove(client)


async def analyze_image(img, save_path=None, websocket=None):
    global last_analyzed_image_path
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

    if save_path:
        cv2.imwrite(save_path, img)
        last_analyzed_image_path = save_path  # Atualizar o caminho da última imagem salva
        
        # Enviar imagem via WebSocket
        if websocket:
            with open(save_path, "rb") as image_file:
                image_data = image_file.read()
                encoded_image = base64.b64encode(image_data).decode('utf-8')
                await websocket.send_text(encoded_image)
    
    # Exibir no console o status da análise
    if all_ok:
        await send_message_to_clients("Todos os itens de segurança presentes.", "sec")
    else:
        await send_message_to_clients("Imagem com itens de segurança em falta.", "sec")
    
    return img, all_ok


def generate_frames():
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)
    try:
        person_detected, detection_pause_time, photo_taken, analysis_paused = False, 0, False, False
        pause_printed = False

        while True:
            success, img = cap.read()
            if not success:
                break

            current_time = time.time()

            if not person_detected or (current_time - detection_pause_time > 10):
                if person_detected and not photo_taken:
                    save_path = f"result_photo_{int(current_time)}.jpg"
                    asyncio.run(analyze_image(img, save_path))
                    asyncio.run(send_message_to_clients("Analise volta em 10", "msg"))  # Envia a mensagem
                    photo_taken, analysis_paused, pause_printed = True, True, False
                    pause_start_time = current_time

                if not analysis_paused or (current_time - pause_start_time > 10):
                    analysis_paused = False
                    if not pause_printed:
                        asyncio.run(send_message_to_clients("Análise voltou", "msg"))
                        pause_printed = True

                    results = model_person(img, stream=True, verbose=False, classes=[0])
                    for r in results:
                        for box in r.boxes:
                            if int(box.cls[0]) == 0 and box.conf[0] > 0.5:
                                person_detected, detection_pause_time, photo_taken = True, current_time, False
                                asyncio.run(send_message_to_clients("Pessoa Detectada. Tirando foto em 10 segundos", "msg"))
                                draw_box(img, box, "Pessoa", box.conf[0], (0, 255, 0))

            ret, buffer = cv2.imencode('.jpg', img)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    finally:
        cap.release()



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    last_sent_image = None
    try:
        while True:
            if last_analyzed_image_path != last_sent_image:
                with open(last_analyzed_image_path, "rb") as image_file:
                    image_data = image_file.read()
                    encoded_image = base64.b64encode(image_data).decode('utf-8')
                    # Prefixo "img:" para imagens
                    await websocket.send_text(f"img:{encoded_image}")
                last_sent_image = last_analyzed_image_path
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        clients.remove(websocket)
        print("Cliente desconectado")


@app.get("/", response_class=FileResponse)
def index():
    return FileResponse("index.html")

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
