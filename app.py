# app.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # 1. Importamos a ferramenta de CORS
import requests

GITHUB_API_URL = "https://api.github.com/users/"

app = FastAPI()

# 2. CONFIGURAÇÃO DO CORS
origins = [
    "http://localhost:5173",  # O endereço do nosso frontend React
    # Você pode adicionar outras URLs aqui no futuro, se precisar
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Lista de origens que podem fazer requisições
    allow_credentials=True,
    allow_methods=["*"],    # Permitir todos os métodos (GET, POST, etc.)
    allow_headers=["*"],    # Permitir todos os cabeçalhos
)
# FIM DA CONFIGURAÇÃO DO CORS

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do DevFinder"}

@app.get("/api/v1/search/{username}")
def search_user(username: str):
    try:
        url = f"{GITHUB_API_URL}{username}"
        response = requests.get(url)
        response.raise_for_status()
        
        user_data = response.json()
        return user_data

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Usuário '{username}' não encontrado.")
        raise HTTPException(status_code=response.status_code, detail=str(http_err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro inesperado: {err}")
