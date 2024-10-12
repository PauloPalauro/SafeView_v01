import asyncio
import face_recognition
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
last_analyzed_image_path = None
classNames = ['Capacete', 'Mascara', 'SEM-Capacete', 'SEM-Mascara', 'SEM-Colete', 'Pessoa', 'Colete']


def carregar_base_dados(diretorio_base):
    return {
        os.path.splitext(arquivo)[0]: face_recognition.face_encodings(
            face_recognition.load_image_file(os.path.join(diretorio_base, arquivo)))[0]
        for arquivo in os.listdir(diretorio_base)
        if arquivo.endswith(('.jpg', '.jpeg', '.png')) and face_recognition.face_encodings(
            face_recognition.load_image_file(os.path.join(diretorio_base, arquivo)))
    }


def reconhecer_face(imagem_teste, base_dados):
    img_teste = face_recognition.load_image_file(imagem_teste)
    encodings_faces = face_recognition.face_encodings(img_teste, face_recognition.face_locations(img_teste))

    for face_encoding in encodings_faces:
        distancias = face_recognition.face_distance(list(base_dados.values()), face_encoding)
        indice_melhor = distancias.argmin()
        return list(base_dados.keys())[indice_melhor] if distancias[indice_melhor] < 0.6 else "Desconhecido"
    
    return "Desconhecido"


# Carregar a base de dados de rostos
diretorio_base = '/home/ideal_pad/Documentos/Projetos/SafeView_v01/BackEnd/Site-example/ScreenPhoto/faces'
base_dados = carregar_base_dados(diretorio_base)


def draw_box(img, box, class_name, conf, color):
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
    cvzone.putTextRect(img, f'{class_name} {conf:.2f}', (max(0, x1), max(35, y1)), scale=2, thickness=2, colorB=color, colorT=(255, 255, 255), offset=6)


async def send_message_to_clients(message, prefix):
    for client in clients:
        try:
            await client.send_text(f"{prefix}:{message}")
        except WebSocketDisconnect:
            clients.remove(client)


async def analyze_image(img, save_path=None, websocket=None):
    global last_analyzed_image_path
    all_ok = True

    # Salvar imagem temporária para reconhecimento de rosto
    temp_image_path = "temp_image.jpg"
    cv2.imwrite(temp_image_path, img)
    
    # Reconhecer rosto da pessoa antes da análise YOLO
    nome_pessoa = reconhecer_face(temp_image_path, base_dados)
    if nome_pessoa == "Desconhecido":
        nome_pessoa = "Pessoa desconhecida"
    print(f"Nome reconhecido: {nome_pessoa}")
    
    # Prosseguir com a análise da imagem com o modelo YOLO
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

    # Definir o diretório de destino com base no resultado da análise
    if save_path:
        directory = "ok_result" if all_ok else "not_ok_result"
        os.makedirs(directory, exist_ok=True)
        save_path = os.path.join(directory, os.path.basename(save_path))
        
        # Salvar a imagem no diretório apropriado
        cv2.imwrite(save_path, img)
        last_analyzed_image_path = save_path
        
        # Enviar imagem via WebSocket
        if websocket:
            with open(save_path, "rb") as image_file:
                image_data = image_file.read()
                encoded_image = base64.b64encode(image_data).decode('utf-8')
                await websocket.send_text(encoded_image)
    
    # Enviar mensagem de status
    if all_ok:
        await send_message_to_clients(f"Todos os itens de segurança presentes para {nome_pessoa}.", "sec")
    else:
        await send_message_to_clients(f"Imagem com itens de segurança em falta para {nome_pessoa}.", "sec")
    
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
                    asyncio.run(send_message_to_clients("Analise volta em 10", "msg"))
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
