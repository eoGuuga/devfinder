# app.py

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import chromadb
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

# --- CONFIGURAÇÃO INICIAL (CARREGAMENTO ÚNICO) ---

print("Iniciando a API do DevFinder Pro...")

# Carrega o modelo de IA (isso acontece UMA VEZ quando o servidor inicia)
print("Carregando o modelo de IA (all-MiniLM-L6-v2)...")
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Modelo de IA carregado com sucesso.")
except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível carregar o modelo de IA. {e}")
    # Em um app de produção real, você poderia decidir não iniciar se o modelo falhar.

# Conecta-se ao ChromaDB persistente (também acontece UMA VEZ)
print("Conectando ao Banco de Dados Vetorial (ChromaDB)...")
try:
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection(name="github_profiles")
    print("Conexão com ChromaDB estabelecida.")
except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível conectar ao ChromaDB. {e}")
    collection = None # Define a coleção como Nula para que a API possa retornar um erro

# Carrega o GITHUB_TOKEN (para a busca de fallback, se necessário)
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_URL = "https://api.github.com/users/"

# --- INICIALIZAÇÃO DO FASTAPI E CORS ---

app = FastAPI(title="DevFinder Pro API")

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
origins = [frontend_url]

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
    return {"message": "Bem-vindo à API do DevFinder Pro (Busca Neural)"}

@app.get("/api/v1/neural-search")
def neural_search(q: str = Query(..., min_length=3)):
    """
    Recebe uma query de busca (q) em linguagem natural,
    gera um embedding para ela, e busca os perfis mais similares
    no nosso banco de dados vetorial (ChromaDB).
    """
    if collection is None:
        raise HTTPException(status_code=503, detail="Serviço indisponível: Banco de dados vetorial não está carregado.")

    print(f"\nRecebida query de busca neural: '{q}'")
    
    try:
        # 1. Converte a query do usuário em um vetor
        query_embedding = model.encode(q).tolist()
        
        # 2. A MÁGICA: Busca no ChromaDB
        # Busca os 5 resultados mais próximos (n_results=5)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )
        
        # 3. Formata os resultados para enviar ao frontend
        # Nós queremos os 'metadatas' e as 'distances' (scores)
        
        metadatas = results.get('metadatas', [[]])[0]
        distances = results.get('distances', [[]])[0]
        
        # Combina os metadados (info do perfil) com o score de similaridade
        formatted_results = []
        for meta, dist in zip(metadatas, distances):
            meta['score'] = (1 - dist) # Convertemos "distância" em "similaridade" (score)
            formatted_results.append(meta)

        print(f"-> Retornando {len(formatted_results)} resultados.")
        return formatted_results

    except Exception as e:
        print(f"Erro durante a busca neural: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar a busca: {e}")

# (Opcional) Manter a busca antiga por nome exato
@app.get("/api/v1/search/{username}")
def search_user(username: str):
    # ... (o código do endpoint antigo continua aqui, sem alterações)
    pass