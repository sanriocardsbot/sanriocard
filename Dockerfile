FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do bot
COPY . .

# Criar diretório para banco de dados
RUN mkdir -p /app/data

# Comando para executar o bot
CMD ["python", "main.py"]
