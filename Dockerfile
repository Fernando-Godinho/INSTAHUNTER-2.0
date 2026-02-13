# Usar a imagem oficial do Python
FROM python:3.13-slim

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema
RUN apt-get update -qq && \
    apt-get install -y -qq \
    git \
    netcat-traditional \
    build-essential \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho (mais curto e padrão)
WORKDIR /app

# Copiar requirements primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install -q --upgrade pip setuptools wheel && \
    pip install -q -r requirements.txt

# Copiar o restante do código da aplicação
COPY . .

# Criar diretórios necessários e ajustar permissões do entrypoint
RUN mkdir -p /app/media /app/staticfiles /app/data && \
    chmod +x /app/entrypoint.sh

# Expor porta 8000
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Usar o entrypoint para rodar migrações e collectstatic no boot
ENTRYPOINT ["/app/entrypoint.sh"]
