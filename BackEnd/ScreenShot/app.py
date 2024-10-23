import asyncio
import face_recognition
from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, StreamingResponse
import cv2
import numpy as np
from ultralytics import YOLO
import cvzone
import base64
import time
from io import BytesIO
from face_recognition_module import carregar_base_dados, reconhecer_face
from pdf_report import create_pdf_report

app = FastAPI()

clients = []

# Carregar os modelos YOLO
model = YOLO("../YOLO-Weights/ppe.pt")
model_person = YOLO("../YOLO-Weights/yolov8n.pt")
classNames = ['Capacete', 'Mascara', 'SEM-Capacete', 'SEM-Mascara', 'SEM-Colete', 'Pessoa', 'Colete']

# Carregar a base de dados de rostos
diretorio_base = 'faces'
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


async def analyze_image(img, websocket=None):
    all_ok = True

    # Converter imagem para formato que o face_recognition pode usar
    temp_image = cv2.imencode('.jpg', img)[1].tobytes()
    temp_buffer = BytesIO(temp_image)

    # Reconhecimento facial
    nome_pessoa = "Pessoa desconhecida"
    try:
        face_image = face_recognition.load_image_file(temp_buffer)
        encodings_faces = face_recognition.face_encodings(face_image, face_recognition.face_locations(face_image))
        
        for face_encoding in encodings_faces:
            distancias = face_recognition.face_distance(list(base_dados.values()), face_encoding)
            if len(distancias) > 0:
                indice_melhor = distancias.argmin()
                if distancias[indice_melhor] < 0.6:
                    nome_pessoa = list(base_dados.keys())[indice_melhor]
    except Exception as e:
        print(f"Erro no reconhecimento facial: {e}")
    
    # Análise YOLO
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

    # Enviar imagem analisada para todos os clientes WebSocket
    _, buffer = cv2.imencode('.jpg', img)
    encoded_image = base64.b64encode(buffer).decode('utf-8')
    await send_message_to_clients(encoded_image, "img")

    # Enviar mensagem de status
    if all_ok:
        await send_message_to_clients(f"Todos os itens de segurança presentes para {nome_pessoa}.", "sec")
    else:
        await send_message_to_clients(f"Imagem com itens de segurança em falta para {nome_pessoa}.", "sec")

    # Criar PDF diretamente da imagem em memória
    pdf_output_path = create_pdf_report(nome_pessoa, all_ok, img)
    print(f"Relatório PDF criado: {pdf_output_path}")
    
    return img, all_ok, pdf_output_path


def generate_frames():
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)
    
    try:
        person_detected = False
        detection_pause_time = 0
        photo_taken = False
        analysis_paused = False
        pause_printed = False

        while True:
            success, img = cap.read()
            if not success:
                break

            current_time = time.time()

            if not person_detected or (current_time - detection_pause_time > 10):
                if person_detected and not photo_taken:
                    asyncio.run(analyze_image(img))
                    asyncio.run(send_message_to_clients("Analise volta em 10 segundos", "msg"))
                    photo_taken = True
                    analysis_paused = True
                    pause_printed = False
                    pause_start_time = current_time

                if not analysis_paused or (current_time - pause_start_time > 10):
                    analysis_paused = False
                    if not pause_printed:
                        asyncio.run(send_message_to_clients("Análise Disponivel", "msg"))
                        pause_printed = True

                    results = model_person(img, stream=True, verbose=False, classes=[0])
                    for r in results:
                        for box in r.boxes:
                            if int(box.cls[0]) == 0 and box.conf[0] > 0.5:
                                person_detected = True
                                detection_pause_time = current_time
                                photo_taken = False
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
    try:
        while True:
            # Aguardar mensagens do cliente (se necessário)
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
