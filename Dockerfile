# Use uma imagem oficial de Python
FROM python:3.10-slim-buster

# Definir a variável de ambiente para evitar que o Python gere arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalar dependências
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

# Copiar o conteúdo do diretório atual para o container
COPY ./ /app/

# Executar a aplicação
CMD ["uvicorn", "Chat:chatapp", "--host", "0.0.0.0", "--port", "7000", "--reload"]

# run the container's build with the command "sudo docker build -t fastapi_chat ." at the root
# run this container with the command "sudo docker run --env-file .env  --name fastapi --network host -v $(pwd):/app fastapi_chat"
