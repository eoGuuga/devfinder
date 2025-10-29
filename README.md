# DevFinder Pro API 🚀

High-performance backend API for DevFinder Pro, built with FastAPI (Python). Provides semantic search capabilities for GitHub developer profiles using AI embedding models and the Pinecone vector database.

**[➡️ Live API (Hugging Face)](https://eoGuuga-devfinder-api.hf.space)** | **[➡️ Live Frontend (Render)](https://devfinder-3w8r.onrender.com)**

## 📖 About

This API serves as the intelligent core of the DevFinder Pro application. It exposes endpoints to perform two types of searches:

1.  **Semantic Neural Search (`/api/v1/neural-search`):** Accepts a natural language query (e.g., "senior react developer with fintech experience"), vectorizes it using a Sentence Transformer model, and queries a **Pinecone** vector index to find the most semantically similar GitHub developer profiles previously indexed.
2.  **Direct Username Lookup (`/api/v1/user/{username}`):** Fetches profile data directly from the GitHub API for a specific username in real-time.

This decoupled architecture allows the API to be consumed by any frontend client (currently, a separately hosted React SPA). The primary focus is enabling efficient discovery of relevant developers based on skills and project descriptions, beyond simple keyword matching.

---

## ✨ Core Features

- **Hybrid Search:** Offers both semantic (AI-powered) discovery and direct username lookup.
- **Semantic Neural Search:** Leverages `sentence-transformers` and Pinecone for concept-based profile retrieval.
- **Pinecone Integration:** Uses a cloud-managed Pinecone index for fast and scalable vector search.
- **Direct GitHub API Integration:** Fetches real-time data for specific users, including recent repositories.
- **FastAPI Framework:** Built for high performance, asynchronous capabilities, and automatic data validation.
- **Automatic API Documentation:** Interactive Swagger UI available at `/docs`.
- **CORS Configuration:** Allows requests from configured frontend origins (local development and production).
- **Dockerized:** Containerized for consistent deployment environments (hosted on Hugging Face Spaces).

---

## 🛠️ Tech Stack

- **Python 3.11+**
- **FastAPI:** High-performance web framework.
- **SentenceTransformers:** Library for generating text embeddings (`paraphrase-MiniLM-L3-v2`).
- **Pinecone:** Cloud-managed vector database.
- **Requests:** For consuming the GitHub API.
- **Uvicorn / Gunicorn:** ASGI/WSGI servers.
- **Docker:** Containerization for deployment.
- **Hugging Face Spaces:** Hosting platform for the containerized API.
- **Environment Variables (`python-dotenv`):** Secure management of API keys (GitHub, Pinecone).

---

## 🚀 Running Locally

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/eoGuuga/devfinder.git](https://github.com/eoGuuga/devfinder.git)
    cd devfinder
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Linux/macOS/Git Bash:
    source venv/bin/activate 
    # On Windows PowerShell:
    .\venv\Scripts\Activate.ps1
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure Environment Variables:**
    * Create a `.env` file in the project root.
    * Add the following keys with your actual values:
      ```
      GITHUB_TOKEN=ghp_YOUR_VALID_GITHUB_TOKEN
      PINECONE_API_KEY=YOUR_PINECONE_API_KEY
      PINECONE_ENVIRONMENT=YOUR_PINECONE_ENVIRONMENT 
      # FRONTEND_URL=http://localhost:5173 (Optional, for local CORS)
      ```
5.  **Run the Indexer (Required only once or to update Pinecone):**
    * Ensure you have created an index in Pinecone named `devfinder-profiles` (dimension: 384, metric: cosine).
    ```bash
    python indexer.py 
    ```
6.  **Start the API server:**
    ```bash
    uvicorn app:app --reload
    ```
7.  The API will be available at `http://127.0.0.1:8000` and the documentation at `http://127.0.0.1:8000/docs`.

---

## 👨‍💻 Author

Developed with 🐍 by **Gustavo Henrick**.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/gustavo-henrick-dev20/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/eoGuuga)