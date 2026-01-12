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

# Definir diretório de trabalho
WORKDIR /workspace/instahunter

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install -q --upgrade pip setuptools wheel && \
    pip install -q -r requirements.txt && \
    pip install -q gunicorn whitenoise

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p /workspace/instahunter/media \
    /workspace/instahunter/staticfiles \
    /workspace/instahunter/data

# Executar migrações e collectstatic
RUN python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput --clear

# Expor porta
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Comando de inicialização
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "sync", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "instahunter.wsgi:application"]
