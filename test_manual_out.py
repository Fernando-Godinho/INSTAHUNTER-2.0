import requests
import json

# URL do seu webhook local
URL = "http://localhost:8000/webhook/waba/"

# Simulação de um log enviado pelo n8n quando a Maria responde
payload = {
    "direction": "OUT",
    "contact_number": "5551983097389",
    "text": "Olá! Esta é uma resposta automática da Maria logada via n8n."
}

try:
    response = requests.post(URL, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Erro: {e}")
