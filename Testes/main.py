import face_recognition
import cv2
import os

def carregar_base_dados(diretorio_base):
    # Dicionário para armazenar os nomes e codificações faciais
    base_dados = {}

    # Percorrer todas as imagens no diretório da base de dados
    for arquivo in os.listdir(diretorio_base):
        # Verificar se o arquivo é uma imagem (extensão pode variar)
        if arquivo.endswith(('.jpg', '.jpeg', '.png')):
            caminho_imagem = os.path.join(diretorio_base, arquivo)
            
            # Carregar a imagem e obter a codificação facial
            imagem = face_recognition.load_image_file(caminho_imagem)
            encodings = face_recognition.face_encodings(imagem)
            
            # Se a imagem tiver uma face detectada, adicionar à base de dados
            if encodings:
                nome = os.path.splitext(arquivo)[0]  # Nome é o nome do arquivo sem a extensão
                base_dados[nome] = encodings[0]
    
    return base_dados

def reconhecer_face(imagem_teste, base_dados):
    # Carregar a imagem de teste
    img_teste = face_recognition.load_image_file(imagem_teste)

    # Detectar as faces na imagem de teste
    locais_faces = face_recognition.face_locations(img_teste)
    encodings_faces = face_recognition.face_encodings(img_teste, locais_faces)

    # Carregar a imagem com OpenCV para exibir as caixas de detecção
    img_teste_bgr = cv2.imread(imagem_teste)

    # Percorrer cada rosto detectado e verificar a correspondência com a base de dados
    for (top, right, bottom, left), face_encoding in zip(locais_faces, encodings_faces):
        # Comparar o rosto detectado com os rostos na base de dados
        resultados = face_recognition.compare_faces(list(base_dados.values()), face_encoding)
        distancias = face_recognition.face_distance(list(base_dados.values()), face_encoding)

        # Obter o índice da menor distância (melhor correspondência)
        melhor_correspondencia = None
        if resultados:
            indice_melhor = distancias.argmin()
            melhor_correspondencia = list(base_dados.keys())[indice_melhor]
        
        # Se houver uma correspondência suficientemente boa, desenhe uma caixa ao redor do rosto
        if resultados[indice_melhor]:
            cv2.rectangle(img_teste_bgr, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(img_teste_bgr, melhor_correspondencia, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        else:
            cv2.rectangle(img_teste_bgr, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(img_teste_bgr, "Desconhecido", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Exibir o resultado e aguardar o fechamento da janela
    cv2.imshow('Resultado', img_teste_bgr)

    # Adicionar um loop para capturar o evento de fechamento
    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if cv2.getWindowProperty('Resultado', cv2.WND_PROP_VISIBLE) < 1:
            break

    # Fechar a janela e liberar recursos
    cv2.destroyAllWindows()

# Uso do código:
# Substitua 'diretorio_base' com o caminho do diretório onde estão as imagens da base de dados.
# Substitua 'imagem_teste.jpg' com o caminho da imagem que deseja testar.
diretorio_base = '/home/ideal_pad/Documentos/Projetos/SafeView_v01/Testes/img'

imagem_teste = '/home/ideal_pad/Documentos/Projetos/SafeView_v01/Testes/aa/folk.jpeg'

# Carregar a base de dados
base_dados = carregar_base_dados(diretorio_base)

# Realizar o reconhecimento facial na imagem de teste
reconhecer_face(imagem_teste, base_dados)
