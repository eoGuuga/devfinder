# indexer.py (Versão Limpa - Pinecone v4+)

import requests
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
from pinecone import Pinecone, PodSpec
import time

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")

if not GITHUB_TOKEN or not PINECONE_API_KEY or not PINECONE_ENVIRONMENT:
    raise EnvironmentError("Variáveis GITHUB_TOKEN, PINECONE_API_KEY ou PINECONE_ENVIRONMENT não encontradas no .env")

headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {GITHUB_TOKEN}"
}
GITHUB_API_URL = "https://api.github.com/users/"
INDEX_NAME = "devfinder-profiles"
MODEL_DIMENSIONS = 384

print("Carregando o modelo de IA (paraphrase-MiniLM-L3-v2)...")
model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
print("Modelo carregado.")

print(f"Conectando ao Pinecone (Ambiente: {PINECONE_ENVIRONMENT})...")
index = None
try:
    print("Inicializando cliente Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)

    print(f"Tentando conectar diretamente ao índice '{INDEX_NAME}'...")
    index = pc.Index(INDEX_NAME)
    print(f"Conexão ao índice '{INDEX_NAME}' estabelecida. Verificando status...")

    print("Aguardando índice ficar pronto...")
    while not pc.describe_index(INDEX_NAME).status['ready']:
        print("Índice ainda não está pronto, aguardando 5 segundos...")
        time.sleep(5)
    print("Índice está pronto.")

    print("Limpando índice existente (se houver dados)...")
    try:
        stats_before = index.describe_index_stats()
        vector_count = getattr(stats_before, 'total_vector_count', 0)
        if vector_count > 0:
             index.delete(delete_all=True)
             print("Aguardando limpeza do índice...")
             time.sleep(10)
             print("Índice limpo.")
        else:
            print("Índice já está vazio.")
    except Exception as del_err:
        print(f"Aviso: Não foi possível limpar o índice completamente: {del_err}")

except Exception as e:
    print(f"ERRO CRÍTICO ao conectar ou verificar o índice '{INDEX_NAME}' no Pinecone: {e}")
    print("Verifique se o nome do índice está correto e se ele foi criado no painel do Pinecone.")
    exit()

def build_semantic_document(username):
    print(f"\nBuscando dados de: {username}")
    user_url = f"{GITHUB_API_URL}{username}"
    repos_url = f"{GITHUB_API_URL}{username}/repos?sort=updated&per_page=5"

    try:
        user_response = requests.get(user_url, headers=headers)
        user_response.raise_for_status()
        user_data = user_response.json()

        bio = user_data.get('bio', '') or ''
        location = user_data.get('location', '') or ''
        name = user_data.get('name', '') or ''

        repos_response = requests.get(repos_url, headers=headers)
        repos_response.raise_for_status()
        repos_data = repos_response.json()

        document_parts = [name, location, bio]
        for repo in repos_data:
            repo_desc = repo.get('description', '') or ''
            repo_lang = repo.get('language', '') or ''
            document_parts.append(f"Projeto: {repo.get('name')}. Descrição: {repo_desc}. Linguagem: {repo_lang}.")

        semantic_document = ". ".join(filter(None, document_parts))

        metadata = {
            "username": user_data.get('login'),
            "name": name,
            "html_url": user_data.get('html_url'),
            "avatar_url": user_data.get('avatar_url'),
            "bio": bio,
            "document_text": semantic_document[:500]
        }

        print(f"-> Documento para {username} construído (Tamanho: {len(semantic_document)} caracteres)")
        return semantic_document, metadata, user_data.get('login')

    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar {username}: {e}")
        return None, None, None

USERNAMES_TO_INDEX = ["eoGuuga", "torvalds", "fabpot", "gaearon", "karpathy", "shadcn", "wesbos", "fireship-io", "jessfraz", "geohot"]

print("\n--- Iniciando construção da Base de Dados Vetorial no Pinecone ---")
vectors_to_upsert = []

for username in USERNAMES_TO_INDEX:
    document, metadata, user_id = build_semantic_document(username)
    if document:
        embedding = model.encode(document).tolist()
        vectors_to_upsert.append((user_id, embedding, metadata))

if vectors_to_upsert:
    try:
        print(f"\nEnviando {len(vectors_to_upsert)} vetores para o Pinecone...")
        index.upsert(vectors=vectors_to_upsert)
        print("--- Indexação no Pinecone concluída com sucesso! ---")

        time.sleep(5)
        stats = index.describe_index_stats()
        print("\nEstatísticas do Índice no Pinecone:")
        print(stats)

    except Exception as e:
        print(f"ERRO ao enviar dados para o Pinecone: {e}")
else:
    print("\n--- Nenhum perfil foi processado para indexação. ---")