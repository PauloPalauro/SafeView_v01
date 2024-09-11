from fastapi import FastAPI, HTTPException,status, Request
from firebase_config import db
from fastapi.responses import JSONResponse
import requests
import bcrypt

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

from fastapi import FastAPI, HTTPException, status, Request
from firebase_config import db
from fastapi.responses import JSONResponse
import requests
import logging

app = FastAPI()

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get('/usuarios')
async def todos_usuarios():
    users_ref = db.collection('usuarios')
    docs = users_ref.stream()
    usuarios = []
    for doc in docs:
        usuario = doc.to_dict()
        print(usuario)  
        usuarios.append(usuario)
    
    return {'usuarios': usuarios}

@app.post('/registra_usuario_padrao')
async def registra_usuario(request: Request):
    try:
        logger.info("Recebendo requisição para registrar usuário...") 

        info = await request.json()
        logger.info(f"Dados recebidos: {info}")  

        email = info.get('email')
        nome = info.get('nome')
        senha = info.get('senha')
        senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

        if not email or not nome or not senha:
            logger.error("Email,nome ou senha não fornecidos.")
            raise HTTPException(status_code=400, detail="Email e nome são obrigatórios.")

        # Referência à coleção de usuários
        users_ref = db.collection('usuarios')
        
        # Verificar se já existe um usuário com o mesmo email
        logger.info(f"Verificando se o usuário com email {email} já existe...")
        docs = users_ref.where('Email', '==', email).stream()
        for doc in docs:
            if doc.exists:
                logger.error(f"Usuário com email {email} já existe.")
                raise HTTPException(status_code=400, detail="Usuário com este email já existe.")
        
        # Adicionar novo usuário ao Firestore
        logger.info("Criando novo usuário...")
        new_user_ref = users_ref.document()
        new_user_ref.set({
            'Email': email,
            'Nome': nome,
            'Admin': False,
            'Senha': senha
        })
        logger.info(f"Usuário {nome} cadastrado com sucesso com ID {new_user_ref.id}")
        return JSONResponse({'mensagem': 'Usuário cadastrado com sucesso', 'user_id': new_user_ref.id}, status_code=201)
    
    except HTTPException as http_exc:
        logger.error(f"Erro HTTP: {http_exc.detail}")
        return JSONResponse({'detail': str(http_exc.detail)}, status_code=http_exc.status_code)
    
    except Exception as e:
        logger.error(f"Ocorreu um erro ao registrar o usuário: {e}")
        return JSONResponse({'mensagem': 'Ocorreu um erro ao registrar o usuário', 'erro': str(e)}, status_code=500)

