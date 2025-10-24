# Usa uma imagem oficial do Python como base
FROM python:3.11-slim 

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de requisitos para dentro do container
COPY requirements.txt requirements.txt

# Instala as dependências, incluindo Gunicorn (sem cache para garantir versões corretas)
# E atualiza o pip primeiro
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt gunicorn

# Copia todo o resto do código da sua aplicação para dentro do container
COPY . .

# Expõe a porta que o FastAPI/Uvicorn/Gunicorn usará (convenção: 8000)
EXPOSE 8000

# O comando que será executado quando o container iniciar
# Usamos Gunicorn com UvicornWorker para rodar o FastAPI em produção
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "app:app", "--bind", "0.0.0.0:8000"]