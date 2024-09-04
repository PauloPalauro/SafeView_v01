from fastapi import FastAPI, HTTPException,status
from firebase_config import db
from fastapi.responses import JSONResponse
import requests

app = FastAPI()
@app.get('/usuarios')
async def todos_usuarios():
    users_ref = db.collection('usuarios')
    docs = users_ref.stream()
    
    usuarios = []
    for doc in docs:
        usuario = doc.to_dict()
        print(usuario)  # Adicione esta linha para verificar os dados no terminal
        usuarios.append(usuario)
    
    return {'usuarios': usuarios}

@app.post('/registra_usuario')
async def registra_usuario(request):
    try:
        info = request.data
        email = info.get('email')
        nome = info.get('nome')
        users_ref = db.collection('usuarios')
        doc_ref = users_ref.document()
        doc_ref.set({
            'Email': email,
            'Nome': nome,
            'Admin': False
        })
        users_ref = db.collection('usuarios')
        
        # Verificar se já existe um usuário com o mesmo email
        docs = users_ref.where('email', '==', usuario.email).stream()
        for doc in docs:
            if doc.exists:
                raise HTTPException(status_code=400, detail="Usuário com este email já existe.")
        
        # Adicionar novo usuário ao Firestore
        new_user_ref = users_ref.document()  # Gera um novo ID para o documento
        new_user_ref.set(usuario.dict())  # Converte o modelo de usuário para um dicionário e salva no Firestore
        return JSONResponse({'mensagem': 'Usuário cadastrado com sucesso'}, status_code=201)
    except Exception as e:
        return {'message': 'Usuário registrado com sucesso', 'user_id': new_user_ref.id}

