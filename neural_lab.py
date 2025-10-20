# neural_lab.py

import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
from dotenv import load_dotenv

# --- CONFIGURAÇÃO INICIAL ---

# Carrega as variáveis de ambiente (o nosso GITHUB_TOKEN) do arquivo .env
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# 1. Carregamos o modelo de IA
print("Carregando o modelo de IA (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Modelo carregado.")

# 2. Configuração da API do GitHub
if not GITHUB_TOKEN:
    print("AVISO: GITHUB_TOKEN não definido. Usando API pública (limite de 60 reqs/hora).")
    headers = {"Accept": "application/vnd.github.v3+json"}
else:
    print("Usando GITHUB_TOKEN para limite de 5000 reqs/hora.")
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}"
    }

# --- FUNÇÃO PRINCIPAL DE CONSTRUÇÃO DO DOCUMENTO ---

def build_semantic_document(username):
    """
    Busca o usuário e seus 5 repositórios mais relevantes no GitHub
    e constrói um "Documento Semântico Composto".
    """
    print(f"\nBuscando dados de: {username}")
    user_url = f"https://api.github.com/users/{username}"
    repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=5"
    
    try:
        # 3. Buscar dados do usuário
        user_response = requests.get(user_url, headers=headers)
        user_response.raise_for_status() # Lança um erro se a requisição falhar
        user_data = user_response.json()
        
        bio = user_data.get('bio', '') or ''
        location = user_data.get('location', '') or ''
        name = user_data.get('name', '') or ''
        
        # 4. Buscar dados dos repositórios
        repos_response = requests.get(repos_url, headers=headers)
        repos_response.raise_for_status()
        repos_data = repos_response.json()
        
        # 5. A MÁGICA: Criar o "Documento Semântico Composto"
        document_parts = [name, location, bio]
        
        for repo in repos_data:
            repo_desc = repo.get('description', '') or ''
            repo_lang = repo.get('language', '') or ''
            document_parts.append(f"Projeto: {repo.get('name')}. Descrição: {repo_desc}. Linguagem: {repo_lang}.")
            
        # Filtra partes vazias e junta tudo em um super-texto
        semantic_document = ". ".join(filter(None, document_parts))
        
        print(f"-> Documento para {username} construído (Tamanho: {len(semantic_document)} caracteres)")
        return semantic_document, user_data.get('html_url')

    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar {username}: {e}")
        return None, None

# --- EXECUÇÃO DO EXPERIMENTO ---

# 6. Lista de usuários para nossa "base de dados" de teste
USERNAMES_TO_INDEX = ["eoGuuga", "torvalds", "fabpot", "gaearon", "karpathy", "SDR-Tasks"]

# 7. Construir nosso "banco de dados" de embeddings
print("\n--- Iniciando construção da Base de Dados Vetorial ---")
database_documents = []
profile_map = {} # Para guardar os dados extras (username, html_url)

for username in USERNAMES_TO_INDEX:
    document, html_url = build_semantic_document(username)
    if document:
        database_documents.append(document)
        # Usamos o documento como chave (temporariamente) para achar os dados
        profile_map[document] = (username, html_url) 
        
print("--- Base de Dados Vetorial construída com sucesso! ---")
        
# 8. Converter todos os documentos em vetores de IA
database_embeddings = model.encode(database_documents)

# 9. Definir a busca do usuário (em linguagem natural)
query = "um estudante de são paulo que gosta de python e internet das coisas"
# query = "o criador do linux"
# query = "especialista em deep learning e redes neurais"
# query = "desenvolvedor que entende de react e frontend"

print(f"\n--- EXECUTANDO BUSCA NEURAL ---")
print(f"Query: '{query}'")
print("-" * 40)

# 10. Converter a busca em um vetor
query_embedding = model.encode(query)

# 11. Calcular a similaridade
similarities = cosine_similarity(
    [query_embedding],
    database_embeddings
)[0]

# 12. Ordenar e exibir os resultados
results = zip(database_documents, similarities)
sorted_results = sorted(results, key=lambda item: item[1], reverse=True)

print("Resultados da Busca Neural (mais relevantes primeiro):")
for doc, score in sorted_results:
    username, html_url = profile_map[doc]
    print(f"\nScore: {score:.4f} - Perfil: {username} ({html_url})")
    print(f"  Trecho do Documento Analisado: {doc[:250]}...")
print("--- FIM DA BUSCA ---")