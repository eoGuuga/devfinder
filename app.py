# app.py

from fastapi import FastAPI, HTTPException
import requests

# Constante para a URL base da API do GitHub
GITHUB_API_URL = "https://api.github.com/users/"

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do DevFinder"}

# Novo endpoint para buscar um usuário
# {username} é um "path parameter": o valor na URL será passado para a função
@app.get("/api/v1/search/{username}")
def search_user(username: str):
    # O "username: str" é uma type hint, dizendo que esperamos que o username seja uma string
    try:
        url = f"{GITHUB_API_URL}{username}"
        response = requests.get(url)
        response.raise_for_status()  # Gera um erro para respostas ruins (404, 500, etc.)
        
        user_data = response.json()
        return user_data

    except requests.exceptions.HTTPError as http_err:
        # Se o usuário não for encontrado (erro 404), retornamos um erro 404 claro
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Usuário '{username}' não encontrado.")
        # Para outros erros HTTP, retornamos o erro original
        raise HTTPException(status_code=response.status_code, detail=str(http_err))
    except Exception as err:
        # Para qualquer outro tipo de erro (ex: problema de rede)
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro inesperado: {err}")