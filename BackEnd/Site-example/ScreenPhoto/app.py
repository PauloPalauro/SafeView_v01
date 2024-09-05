from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
import cv2
import numpy as np
from ultralytics import YOLO
import cvzone
import math
import base64

app = FastAPI()

# Carregar o modelo YOLO
model = YOLO("../../YOLO-Weights/ppe.pt")
classNames = ['Capacete', 'Mascara', 'SEM-Capacete', 'SEM-Mascara', 'SEM-Colete', 'Pessoa', 'Colete']

def analyze_image(img):
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
                if currentClass in ['SEM-Capacete', 'SEM-Colete', 'SEM-Mascara']:
                    myColor = (0, 0, 255)  # Vermelho
                elif currentClass in ['Capacete', 'Colete', 'Mascara']:
                    myColor = (0, 255, 0)  # Verde
                else:
                    myColor = (255, 0, 0)  # Azul

                # Desenhar caixa delimitadora e etiqueta
                cvzone.putTextRect(img, f'{classNames[cls]} {conf}',
                                   (max(0, x1), max(35, y1)), scale=2, thickness=2,
                                   colorB=myColor, colorT=(255, 255, 255), colorR=myColor, offset=6)
                cv2.rectangle(img, (x1, y1), (x2, y2), myColor, 3)

    return img

class ImageData(BaseModel):
    image: str

@app.get("/", response_class=FileResponse)
async def index():
    # Certifique-se de que o caminho para o index.html esteja correto
    return FileResponse("index.html")

@app.post("/analyze_image")
async def analyze_image_endpoint(image_data: ImageData):
    # Decodificar a imagem base64 recebida
    image_bytes = base64.b64decode(image_data.image.split(",")[1])
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Analisar a imagem usando o modelo YOLO
    analyzed_img = analyze_image(img)

    # Converter a imagem analisada para JPEG
    ret, buffer = cv2.imencode('.jpg', analyzed_img)
    if not ret:
        return {"error": "Failed to encode image"}

    # Retornar a imagem como uma resposta HTTP
    return Response(content=buffer.tobytes(), media_type="image/jpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
