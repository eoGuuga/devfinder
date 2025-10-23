# app.py

import requests
import os
import chromadb
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# --- CONFIGURAÇÃO INICIAL (CARREGAMENTO ÚNICO) ---
print("Iniciando a API do DevFinder Pro...")

# Carrega as variáveis de ambiente (o GITHUB_TOKEN)
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise EnvironmentError("GITHUB_TOKEN não encontrado no arquivo .env")

# Configuração dos cabeçalhos da API do GitHub
headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {GITHUB_TOKEN}"
}
GITHUB_API_URL = "https://api.github.com/users/"

# 1. Carregamos o modelo de IA (isso acontece UMA VEZ quando o servidor inicia)
print("Carregando o modelo de IA (all-MiniLM-L6-v2)...")
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Modelo de IA carregado com sucesso.")
except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível carregar o modelo de IA. {e}")
    model = None

# 2. Criamos um cliente ChromaDB EM MEMÓRIA
# Em vez de PersistentClient(path=...), usamos Client()
try:
    client = chromadb.Client() # Cliente em memória
    collection = client.create_collection(name="github_profiles")
    print("Banco de dados vetorial em memória criado.")
except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível criar a coleção do ChromaDB. {e}")
    collection = None

# --- INICIALIZAÇÃO DO FASTAPI E CORS ---

app = FastAPI(title="DevFinder Pro API")

# Lógica de "Startup": Isso roda UMA VEZ quando o FastAPI inicia
@app.on_event("startup")
def load_and_index_data():
    if model is None or collection is None:
        print("ERRO: Modelo ou Coleção não inicializados. Indexação abortada.")
        return

    print("\n--- INICIANDO PROCESSO DE INDEXAÇÃO EM MEMÓRIA ---")
    USERNAMES_TO_INDEX = ["eoGuuga", "torvalds", "fabpot", "gaearon", "karpathy", "shadcn", "wesbos", "fireship-io", "jessfraz", "geohot"]
    
    documents_to_add = []
    metadatas_to_add = []
    ids_to_add = []

    for username in USERNAMES_TO_INDEX:
        print(f"Processando: {username}")
        try:
            # 1. Buscar dados do usuário
            user_url = f"{GITHUB_API_URL}{username}"
            repos_url = f"{GITHUB_API_URL}{username}/repos?sort=updated&per_page=5"
            
            user_response = requests.get(user_url, headers=headers)
            user_response.raise_for_status()
            user_data = user_response.json()
            
            # 2. Buscar dados dos repositórios
            repos_response = requests.get(repos_url, headers=headers)
            repos_response.raise_for_status()
            repos_data = repos_response.json()
            
            # 3. Construir Documento Semântico
            bio = user_data.get('bio', '') or ''
            location = user_data.get('location', '') or ''
            name = user_data.get('name', '') or ''
            
            document_parts = [name, location, bio]
            for repo in repos_data:
                repo_desc = repo.get('description', '') or ''
                repo_lang = repo.get('language', '') or ''
                document_parts.append(f"Projeto: {repo.get('name')}. Descrição: {repo_desc}. Linguagem: {repo_lang}.")
            
            semantic_document = ". ".join(filter(None, document_parts))
            
            # 4. Preparar dados para o Chroma
            metadata = {
                "username": user_data.get('login'),
                "name": name,
                "html_url": user_data.get('html_url'),
                "avatar_url": user_data.get('avatar_url'),
                "bio": bio
            }
            
            documents_to_add.append(semantic_document)
            metadatas_to_add.append(metadata)
            ids_to_add.append(user_data.get('login'))
        
        except requests.exceptions.RequestException as e:
            print(f"AVISO: Falha ao buscar dados para {username}: {e}")

    # 5. Adicionar tudo ao ChromaDB de uma vez
    if documents_to_add:
        # O ChromaDB usará o 'model' que passamos para criar os embeddings
        embeddings = model.encode(documents_to_add)
        
        collection.add(
            embeddings=embeddings,
            documents=documents_to_add,
            metadatas=metadatas_to_add,
            ids=ids_to_add
        )
        print(f"--- Indexação em memória concluída! {len(documents_to_add)} perfis carregados. ---")
    else:
        print("--- Nenhum perfil foi indexado. ---")

# Configuração do CORS

# Nossa URL local de desenvolvimento é sempre permitida
local_url = "http://localhost:5173"

# A URL de produção será lida da variável de ambiente
prod_url = os.getenv("FRONTEND_URL") 

# Crie a lista de origens permitidas
origins = [local_url]
if prod_url:
    # Se a variável de produção existir, adicione-a à lista
    origins.append(prod_url)

print(f"Permitindo conexões CORS de: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # <-- Agora usamos nossa lista dinâmica
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    if collection is None:
        raise HTTPException(status_code=503, detail="Serviço indisponível: Banco de dados vetorial não está carregado.")

    print(f"\nRecebida query de busca neural: '{q}'")
    
    try:
        query_embedding = model.encode(q).tolist()
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )
        
        metadatas = results.get('metadatas', [[]])[0]
        distances = results.get('distances', [[]])[0]
        
        formatted_results = []
        for meta, dist in zip(metadatas, distances):
            meta['score'] = (1 - dist) # Convertemos "distância" em "similaridade"
            formatted_results.append(meta)

        print(f"-> Retornando {len(formatted_results)} resultados.")
        return formatted_results

    except Exception as e:
        print(f"Erro durante a busca neural: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar a busca: {e}")