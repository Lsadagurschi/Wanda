FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Tornar o script de start executável
RUN chmod +x start.sh

# Variáveis de ambiente padrão
ENV FLASK_APP=src/main.py
ENV FLASK_ENV=production
ENV PORT=5000

EXPOSE ${PORT}

# Usa script shell para expandir $PORT em tempo de execução
CMD ["sh", "start.sh"]
