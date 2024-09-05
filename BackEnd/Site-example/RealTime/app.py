from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
import cv2
from ultralytics import YOLO
import cvzone
import math
import time

app = FastAPI()

# Carregar o modelo YOLO
model = YOLO("../../YOLO-Weights/ppe.pt")
classNames = ['Capacete', 'Máscara', 'SEM-Capacete', 'SEM-Máscara', 'SEM-Colete', 'Pessoa', 'Colete']

def generate_frames():
    cap = cv2.VideoCapture(0)  # Inicializar captura de vídeo com a webcam padrão
    cap.set(3, 1280)  # Definir largura
    cap.set(4, 720)   # Definir altura
    
    while True:
        # Capturar frame
        success, img = cap.read()
        if not success:
            break
        
        # Executar o modelo YOLO no frame capturado
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
                    elif currentClass in ['Capacete', 'Colete', 'Máscara']:
                        myColor = (0, 255, 0)  # Verde
                    else:
                        myColor = (255, 0, 0)  # Azul

                    # Desenhar caixa delimitadora e etiqueta
                    cvzone.putTextRect(img, f'{classNames[cls]} {conf}',
                                       (max(0, x1), max(35, y1)), scale=2, thickness=2,
                                       colorB=myColor, colorT=(255, 255, 255), colorR=myColor, offset=6)
                    cv2.rectangle(img, (x1, y1), (x2, y2), myColor, 3)

        # Converter o frame para o formato JPEG
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()

        # Usar gerador para saída de frames
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.get("/", response_class=FileResponse)
async def index():
    # Retorna o arquivo index.html diretamente
    return FileResponse("index.html")

@app.get("/video_feed")
async def video_feed():
    # Gera o feed de vídeo usando StreamingResponse
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
