import firebase_admin
from firebase_admin import db,credentials,firestore

cred = credentials.Certificate(".\\credenciais.json")
firebase_admin.initialize_app(cred)

db = firestore.client()