---
title: DevFinder Pro API
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860 # <-- CORRIGIDO AQUI
pinned: false
---

# DevFinder Pro API 🚀

API de backend para o DevFinder Pro, construída com FastAPI e Python, que fornece funcionalidade de busca semântica para perfis de desenvolvedores do GitHub usando modelos de IA e um banco de dados vetorial.

**[➡️ API Live (Hugging Face)](https://eoGuuga-devfinder-api.hf.space)** | **[➡️ Frontend Live (Render)](https://devfinder-3w8r.onrender.com)**

## 📖 Sobre

Esta API serve como o "cérebro" da aplicação DevFinder Pro. Ela recebe uma query em linguagem natural (ex: "desenvolvedor react de São Paulo com experiência em back-end"), utiliza um modelo de embedding (`sentence-transformers`) para vetorizar a query e consulta um índice vetorial no **Pinecone** para encontrar os perfis de desenvolvedores do GitHub semanticamente mais relevantes.

A arquitetura desacoplada permite que esta API seja consumida por qualquer frontend (atualmente, uma aplicação React hospedada separadamente).

---

## ✨ Funcionalidades Principais

- **Busca Neural Semântica:** Endpoint `/api/v1/neural-search` que aceita uma query (`q`) e retorna uma lista de perfis ranqueados por similaridade semântica.
- **Integração com Pinecone:** Utiliza um índice vetorial hospedado no Pinecone para buscas rápidas e eficientes.
- **Modelo de Embedding:** Usa o modelo `paraphrase-MiniLM-L3-v2` (via `sentence-transformers`) para gerar embeddings de texto.
- **Documentação Automática:** Interface Swagger UI disponível em `/docs` para teste interativo da API.
- **CORS Configurado:** Permite requisições do frontend hospedado.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.11+**
- **FastAPI:** Framework web de alta performance para construção da API.
- **SentenceTransformers:** Biblioteca para gerar embeddings de texto.
- **Pinecone:** Banco de dados vetorial gerenciado na nuvem para armazenar e buscar embeddings.
- **Requests:** Para consumir a API do GitHub durante a indexação (offline).
- **Uvicorn / Gunicorn:** Servidores ASGI/WSGI para rodar a aplicação em desenvolvimento e produção.
- **Docker:** Para containerizar a aplicação para deploy.
- **Hugging Face Spaces:** Plataforma de hospedagem para a API containerizada.
- **Variáveis de Ambiente (`python-dotenv`):** Para gerenciamento seguro de chaves de API.

---

## 🚀 Como Executar Localmente

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/eoGuuga/devfinder.git](https://github.com/eoGuuga/devfinder.git)
    cd devfinder
    ```
2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    # No Linux/macOS/Git Bash:
    source venv/bin/activate 
    # No Windows PowerShell:
    .\venv\Scripts\Activate.ps1
    ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure as Variáveis de Ambiente:**
    * Crie um arquivo `.env` na raiz do projeto.
    * Adicione as seguintes chaves com seus valores:
      ```
      GITHUB_TOKEN=ghp_SEU_TOKEN_GITHUB
      PINECONE_API_KEY=SUA_CHAVE_API_PINECONE
      PINECONE_ENVIRONMENT=SEU_AMBIENTE_PINECONE
      # FRONTEND_URL=http://localhost:5173 (Opcional, para testes locais do CORS)
      ```
5.  **Execute o Indexador (Apenas uma vez ou quando quiser atualizar):**
    * Certifique-se de ter um índice criado no Pinecone com o nome `devfinder-profiles` e dimensão `384`.
    ```bash
    python indexer.py
    ```
6.  **Inicie o servidor da API:**
    ```bash
    uvicorn app:app --reload
    ```
7.  A API estará disponível em `http://127.0.0.1:8000` e a documentação em `http://127.0.0.1:8000/docs`.

---

## 👨‍💻 Autor

Feito com ❤️ por **Gustavo Henrick**.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/gustavo-henrick-dev20/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/eoGuuga)