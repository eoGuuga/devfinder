# app.py (Versão Final com Pinecone)

import requests
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from pinecone import Pinecone # Importação do Pinecone

# --- CONFIGURAÇÃO INICIAL (CARREGAMENTO ÚNICO) ---
print("Iniciando a API do DevFinder Pro...")

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT") # Adicionamos o ambiente
INDEX_NAME = "devfinder-profiles" # Nome do índice Pinecone

if not PINECONE_API_KEY or not PINECONE_ENVIRONMENT:
    raise EnvironmentError("PINECONE_API_KEY ou PINECONE_ENVIRONMENT não encontradas no .env")

# 1. Carregamos o modelo de IA (só para encodar a query)
print("Carregando o modelo de IA (paraphrase-MiniLM-L3-v2)...")
try:
    model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
    print("Modelo de IA carregado com sucesso.")
except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível carregar o modelo de IA. {e}")
    model = None

# 2. Conectamos ao Pinecone (Conexão Direta v4+)
print(f"Conectando ao Pinecone (Índice: {INDEX_NAME}, Ambiente: {PINECONE_ENVIRONMENT})...")
pinecone_index = None
try:
    print("Inicializando cliente Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY) # Inicializa cliente

    print(f"Tentando conectar diretamente ao índice '{INDEX_NAME}'...")
    # Tenta pegar o objeto do índice diretamente.
    # Se não existir, deve levantar uma exceção clara.
    pinecone_index = pc.Index(INDEX_NAME) 
    print(f"Conexão ao índice '{INDEX_NAME}' estabelecida. Verificando status...")

    # Opcional: Adicionar uma pequena espera para garantir a prontidão
    # time.sleep(2) # Descomente se ainda tiver problemas

    print("Conexão com Pinecone bem-sucedida.")

except Exception as e:
    print(f"ERRO CRÍTICO ao conectar ao índice '{INDEX_NAME}' no Pinecone: {e}")
    print("Verifique se o nome do índice e as credenciais no .env estão corretos.")
    # Mantemos pinecone_index como None se a conexão falhar
    
# (GITHUB_TOKEN ainda pode ser útil para o endpoint antigo, se você o manteve)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_URL = "https://api.github.com/users/"

# --- INICIALIZAÇÃO DO FASTAPI E CORS ---

app = FastAPI(title="DevFinder Pro API")

# Configuração do CORS (simplificada, pois a lógica de múltiplas origens já está no .env)
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
origins = [frontend_url]
# Se você tiver uma URL de produção, adicione-a aqui ou via variável de ambiente
prod_url = os.getenv("PROD_FRONTEND_URL")
if prod_url:
    origins.append(prod_url)

print(f"Permitindo conexões CORS de: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ENDPOINTS DA API ---

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do DevFinder Pro (Busca Neural com Pinecone)"}

@app.get("/api/v1/neural-search")
def neural_search(q: str = Query(..., min_length=3)):
    """
    Recebe uma query de busca (q), gera um embedding,
    e busca os perfis mais similares no índice Pinecone.
    """
    if pinecone_index is None or model is None:
        raise HTTPException(status_code=503, detail="Serviço indisponível: Modelo de IA ou Banco Vetorial não carregado.")

    print(f"\nRecebida query de busca neural: '{q}'")

    try:
        # 1. Converte a query do usuário em um vetor
        query_embedding = model.encode(q).tolist()

        # 2. A MÁGICA: Busca no Pinecone
        # Busca os 5 resultados mais próximos, incluindo os metadados
        results = pinecone_index.query(
            vector=query_embedding,
            top_k=5, # Número de resultados a retornar
            include_metadata=True # MUITO IMPORTANTE: Pedimos para incluir os metadados
        )

        # 3. Formata os resultados para enviar ao frontend
        formatted_results = []
        if results.matches:
            for match in results.matches:
                metadata = match.metadata
                # Adiciona o score ao metadado (Pinecone já retorna 'score')
                metadata['score'] = match.score
                formatted_results.append(metadata)

        print(f"-> Retornando {len(formatted_results)} resultados do Pinecone.")
        return formatted_results

    except Exception as e:
        print(f"Erro durante a busca neural no Pinecone: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar a busca: {e}")

# (Opcional) Manter a busca antiga por nome exato
# @app.get("/api/v1/search/{username}")
# def search_user(username: str):
#     # ... (o código do endpoint antigo continua aqui, sem alterações)
#     pass

# Rodar com Uvicorn (apenas para desenvolvimento local)
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)