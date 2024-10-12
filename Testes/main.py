import os
import face_recognition

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
        melhor_correspondencia = list(base_dados.keys())[indice_melhor] if distancias[indice_melhor] < 0.6 else "Desconhecido"
        print(f"Correspondência: {melhor_correspondencia}")

diretorio_base = '/home/ideal_pad/Documentos/Projetos/SafeView_v01/BackEnd/Site-example/ScreenPhoto/faces'
imagem_teste = '/home/ideal_pad/Documentos/Projetos/SafeView_v01/BackEnd/Site-example/ScreenPhoto/faces/paulo.jpeg'

base_dados = carregar_base_dados(diretorio_base)
reconhecer_face(imagem_teste, base_dados)
