#!/bin/sh

# Aguarda o banco de dados se necessário (opcional, mas bom se usar Postgres)
# if [ "$DATABASE_URL" != "" ]; then
#   # Lógica para esperar DB
# fi

echo "Executando migrações..."
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "Iniciando Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 instahunter.wsgi:application
