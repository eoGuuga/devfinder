import requests
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from pinecone import Pinecone

print("Iniciando a API do DevFinder Pro...")

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = "devfinder-profiles"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_URL = "https://api.github.com/users/"

if not PINECONE_API_KEY or not PINECONE_ENVIRONMENT:
    raise EnvironmentError("PINECONE_API_KEY ou PINECONE_ENVIRONMENT não encontradas no .env")

if GITHUB_TOKEN:
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    print("Usando GITHUB_TOKEN.")
else:
    headers = {"Accept": "application/vnd.github.v3+json"}
    print("AVISO: GITHUB_TOKEN não definido. Limites de API podem ser atingidos.")

print("Carregando o modelo de IA (paraphrase-MiniLM-L3-v2)...")
model = None
try:
    model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
    print("Modelo de IA carregado com sucesso.")
except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível carregar o modelo de IA. {e}")

print(f"Conectando ao Pinecone (Índice: {INDEX_NAME}, Ambiente: {PINECONE_ENVIRONMENT})...")
pinecone_index = None
try:
    print("Inicializando cliente Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    print(f"Tentando conectar diretamente ao índice '{INDEX_NAME}'...")
    pinecone_index = pc.Index(INDEX_NAME)
    print(f"Conexão ao índice '{INDEX_NAME}' estabelecida.")
except Exception as e:
    print(f"ERRO CRÍTICO ao conectar ao índice '{INDEX_NAME}' no Pinecone: {e}")
    print("Verifique se o nome do índice e as credenciais no .env estão corretos.")

app = FastAPI(title="DevFinder Pro API")

local_url = "http://localhost:5173"
prod_url = os.getenv("FRONTEND_URL")
origins = [local_url]
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

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do DevFinder Pro (Busca Híbrida)"}

@app.get("/api/v1/neural-search")
def neural_search(q: str = Query(..., min_length=3)):
    if pinecone_index is None or model is None:
        raise HTTPException(status_code=503, detail="Serviço indisponível: Modelo de IA ou Banco Vetorial não carregado.")

    print(f"\nRecebida query de busca neural: '{q}'")
    try:
        query_embedding = model.encode(q).tolist()
        results = pinecone_index.query(
            vector=query_embedding,
            top_k=5,
            include_metadata=True
        )
        formatted_results = []
        if results.matches:
            for match in results.matches:
                metadata = match.metadata
                metadata['score'] = match.score
                formatted_results.append(metadata)
        print(f"-> Retornando {len(formatted_results)} resultados do Pinecone.")
        return formatted_results
    except Exception as e:
        print(f"Erro durante a busca neural no Pinecone: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar a busca neural: {e}")

@app.get("/api/v1/user/{username}")
async def get_user_by_username(username: str):
    print(f"\n[BUSCA DIRETA] Iniciando busca para: '{username}'") # Log 1: Função iniciada
    user_url = f"{GITHUB_API_URL}{username}"
    repos_url = f"{GITHUB_API_URL}{username}/repos?sort=updated&per_page=5"
    local_headers = headers # Usa os headers globais

    print(f"[BUSCA DIRETA] URL do usuário: {user_url}") # Log 2: URL a ser chamada
    print(f"[BUSCA DIRETA] Usando Headers: {local_headers.get('Authorization', 'Nenhum token encontrado')}") # Log 3: Confirma se o token está nos headers

    user_response = None # Inicializa a variável
    try:
        user_response = requests.get(user_url, headers=local_headers)
        
        # Log 4: Resposta CRUCIAL da API do GitHub ANTES de qualquer tratamento
        print(f"[BUSCA DIRETA] Resposta GitHub Status: {user_response.status_code}")
        # print(f"[BUSCA DIRETA] Resposta GitHub Conteúdo: {user_response.text[:500]}...") # Descomente CUIDADOSAMENTE se precisar ver o corpo

        user_response.raise_for_status() # Lança erro para 4xx/5xx
        user_data = user_response.json()

        print("[BUSCA DIRETA] Buscando repositórios...")
        try:
            repos_response = requests.get(repos_url, headers=local_headers)
            # Log 5: Status da busca de repositórios
            print(f"[BUSCA DIRETA] Resposta Repos Status: {repos_response.status_code}")
            repos_response.raise_for_status()
            repos_data = repos_response.json()
            user_data['repositories'] = repos_data
        except requests.exceptions.RequestException as repo_err:
            print(f"[BUSCA DIRETA] Aviso: Não foi possível buscar repositórios para {username}: {repo_err}")
            user_data['repositories'] = []

        print(f"[BUSCA DIRETA] -> Sucesso! Retornando dados de '{username}'.")
        return user_data

    except requests.exceptions.HTTPError as http_err:
        status_code_to_raise = user_response.status_code if user_response is not None else 500
        print(f"[BUSCA DIRETA] ERRO HTTP: Status {status_code_to_raise} - {http_err}") # Log 6: Erro HTTP
        if status_code_to_raise == 404:
            raise HTTPException(status_code=404, detail=f"Usuário '{username}' não encontrado no GitHub.")
        else:
            raise HTTPException(status_code=status_code_to_raise, detail=f"Erro na API do GitHub ao buscar usuário: {http_err}")
    except Exception as err:
        print(f"[BUSCA DIRETA] ERRO Inesperado: {err}") # Log 7: Erro genérico
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro inesperado ao buscar '{username}': {err}")