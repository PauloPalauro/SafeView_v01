from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, Response, JSONResponse, StreamingResponse
from pydantic import BaseModel
import cv2
import numpy as np
from ultralytics import YOLO
import cvzone
import math
import base64
import time

app = FastAPI()

# Carregar o modelo YOLO
model = YOLO("../../YOLO-Weights/ppe.pt")
model_person = YOLO("yolov8n.pt")
model_person.classes = [0]
classNames = ['Capacete', 'Máscara', 'SEM-Capacete', 'SEM-Máscara', 'SEM-Colete', 'Pessoa', 'Colete']

def analyze_image(img):
    # Inicializa uma flag para verificar se tudo está em ordem
    all_ok = True

    # Executar o modelo YOLO na imagem capturada
    results = model(img, stream=True)
    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Caixa delimitadora
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1

            # Confiança
            conf = math.ceil((box.conf[0] * 100)) / 100
            # Nome da Classe
            cls = int(box.cls[0])
            print(f"Índice da classe: {cls}")

            if cls < len(classNames):
                currentClass = classNames[cls]
            else:
                currentClass = "Desconhecido"
            
            print(currentClass)
            
            # Definir cores da caixa delimitadora e do texto
            if conf > 0.5:
                if currentClass in ['SEM-Capacete', 'SEM-Colete', 'SEM-Máscara']:
                    myColor = (0, 0, 255)  # Vermelho
                    all_ok = False  # Se algum item obrigatório estiver faltando, define all_ok como False
                elif currentClass in ['Capacete', 'Colete', 'Máscara']:
                    myColor = (0, 255, 0)  # Verde
                else:
                    myColor = (255, 0, 0)  # Azul

                # Desenhar caixa delimitadora e etiqueta
                cvzone.putTextRect(img, f'{classNames[cls]} {conf}',
                                   (max(0, x1), max(35, y1)), scale=2, thickness=2,
                                   colorB=myColor, colorT=(255, 255, 255), colorR=myColor, offset=6)
                cv2.rectangle(img, (x1, y1), (x2, y2), myColor, 3)

    return img, all_ok


def generate_frames():
    cap = cv2.VideoCapture(0)  # Inicializar captura de vídeo com a webcam padrão
    cap.set(3, 1280)  # Definir largura
    cap.set(4, 720)   # Definir altura
    
    person_detected = False  # Flag para controlar a análise do YOLO
    detection_pause_time = 0  # Tempo de pausa após a detecção

    while True:
        # Capturar frame
        success, img = cap.read()
        if not success:
            break
        
        current_time = time.time()  # Tempo atual

        # Se a pessoa ainda não foi detectada ou a pausa já terminou, executar o modelo YOLO
        if not person_detected or (current_time - detection_pause_time > 10):
            # Resetar a flag após o tempo de pausa
            if person_detected and (current_time - detection_pause_time > 10):
                person_detected = False  # Permitir nova detecção após a pausa

            # Executar o modelo YOLO no frame capturado
            results = model_person(img, stream=True, verbose=False, classes=[0])

            for r in results:
                boxes = r.boxes
                for box in boxes:
                    # Caixa delimitadora
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                    # Confiança
                    conf = math.ceil((box.conf[0] * 100)) / 100
                    # Nome da Classe
                    cls = int(box.cls[0])
                    
                    if cls == 0 and conf > 0.5:  # Verifica se é uma pessoa e se a confiança é alta
                        person_detected = True  # Atualiza a flag se uma pessoa for detectada
                        detection_pause_time = current_time  # Define o tempo da detecção
                        print(f"Pessoa Detectada! Índice da classe: {cls}, Confiança: {conf}")  # Apenas imprime quando uma detecção é encontrada
                        
                        # Definir cor da caixa delimitadora
                        myColor = (0, 255, 0)  # Verde
                        cv2.rectangle(img, (x1, y1), (x2, y2), myColor, 3)

                        # Desenhar texto com a confiança
                        cvzone.putTextRect(img, f'Pessoa {conf:.2f}',  # Exibir confiança
                                           (max(0, x1), max(35, y1)), scale=2, thickness=2,
                                           colorB=myColor, colorT=(255, 255, 255), offset=6)

        # Converter o frame para o formato JPEG
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()

        # Usar gerador para saída de frames
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()



class ImageData(BaseModel):
    image: str

@app.get("/", response_class=FileResponse)
async def index():
    # Certifique-se de que o caminho para o index.html esteja correto
    return FileResponse("index.html")


@app.get("/video_feed")
async def video_feed():
    # Gera o feed de vídeo usando StreamingResponse
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.post("/analyze_image")
async def analyze_image_endpoint(image_data: ImageData):

    # Decodificar a imagem base64 recebida
    image_bytes = base64.b64decode(image_data.image.split(",")[1])
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Analisar a imagem usando o modelo YOLO
    analyzed_img, all_ok = analyze_image(img)

    # Converter a imagem analisada para JPEG
    ret, buffer = cv2.imencode('.jpg', analyzed_img)
    if not ret:
        return {"error": "Failed to encode image"}

    # Retornar a imagem como uma resposta HTTP junto com o status
    return JSONResponse(content={"image": base64.b64encode(buffer.tobytes()).decode('utf-8'), "all_ok": all_ok})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)