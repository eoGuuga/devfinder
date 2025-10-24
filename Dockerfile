# Usa uma imagem oficial do Python como base
FROM python:3.11-slim 

# Cria um usuário não-root por segurança
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de requisitos
COPY --chown=user ./requirements.txt requirements.txt

# Instala as dependências (atualiza pip primeiro)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt gunicorn

# Copia o resto do código da aplicação
COPY --chown=user . /app

# Expõe a porta correta que o Hugging Face espera
EXPOSE 7860

# Comando para iniciar a aplicação na porta correta
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "app:app", "--bind", "0.0.0.0:7860"]