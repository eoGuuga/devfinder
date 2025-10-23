# indexer.py

import requests
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
import chromadb

# --- CONFIGURAÇÃO INICIAL ---
print("Iniciando o processo de indexação...")

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

# 1. Carregamos o modelo de IA
print("Carregando o modelo de IA (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Modelo carregado.")

# 2. Conectamos ao ChromaDB (em modo persistente)
# Isso criará uma pasta chamada 'chroma_db' para armazenar o banco de dados
client = chromadb.PersistentClient(path="./chroma_db")

# 3. Criamos (ou obtemos, se já existir) nossa "coleção" (tabela)
# Usaremos o mesmo modelo de IA para o Chroma saber como lidar com os dados
collection_name = "github_profiles"
try:
    collection = client.get_collection(name=collection_name)
    print(f"Coleção '{collection_name}' já existe. Iremos atualizá-la.")
    # Limpamos a coleção para indexar novamente (opcional, mas bom para testes)
    client.delete_collection(name=collection_name)
    collection = client.create_collection(name=collection_name)
    print("Coleção limpa e recriada.")
except Exception:
    collection = client.create_collection(name=collection_name)
    print(f"Coleção '{collection_name}' criada.")


# --- FUNÇÕES DE BUSCA E PROCESSAMENTO (Igual ao laboratório) ---

def build_semantic_document(username):
    """
    Busca o usuário e seus 5 repositórios mais relevantes no GitHub
    e constrói um "Documento Semântico Composto".
    """
    print(f"\nBuscando dados de: {username}")
    user_url = f"https://api.github.com/users/{username}"
    repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=5"
    
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
        
        # Preparamos os metadados que queremos salvar junto com o vetor
        metadata = {
            "username": user_data.get('login'),
            "name": name,
            "html_url": user_data.get('html_url'),
            "avatar_url": user_data.get('avatar_url'),
            "bio": bio
        }
        
        print(f"-> Documento para {username} construído (Tamanho: {len(semantic_document)} caracteres)")
        return semantic_document, metadata, user_data.get('login')

    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar {username}: {e}")
        return None, None, None

# --- EXECUÇÃO DA INDEXAÇÃO ---

# Lista de usuários para indexar (podemos aumentar muito isso no futuro)
USERNAMES_TO_INDEX = ["eoGuuga", "torvalds", "fabpot", "gaearon", "karpathy", "shadcn", "wesbos", "fireship-io", "jessfraz", "geohot"]

print("\n--- Iniciando construção da Base de Dados Vetorial ---")
documents_to_add = []
metadatas_to_add = []
ids_to_add = []

for username in USERNAMES_TO_INDEX:
    document, metadata, user_id = build_semantic_document(username)
    if document:
        documents_to_add.append(document)
        metadatas_to_add.append(metadata)
        ids_to_add.append(user_id) # Usamos o username como ID único

# 4. A MÁGICA: Adicionando tudo ao ChromaDB de uma vez
# O ChromaDB irá automaticamente:
# 1. Receber os textos (documents)
# 2. Usar o modelo 'all-MiniLM-L6-v2' (que ele conhece) para criar os embeddings
# 3. Salvar os embeddings, os documentos e os metadados
if documents_to_add:
    collection.add(
        documents=documents_to_add,
        metadatas=metadatas_to_add,
        ids=ids_to_add
    )
    print("\n--- Indexação concluída com sucesso! ---")
    print(f"{len(documents_to_add)} perfis foram indexados no ChromaDB.")
else:
    print("\n--- Nenhum perfil foi indexado. ---")