#!/usr/bin/env python
"""
Debug da criação de instância - verificar resposta do QR Code
"""
import os
import sys
import django
import json
import time
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instahunter.settings')
django.setup()

from django.conf import settings

base_url = settings.EVOLUTION_API_URL
api_key = settings.EVOLUTION_API_KEY
headers = {'apikey': api_key, 'Content-Type': 'application/json'}

# Criar instância de teste
instance_name = f'test-debug-{int(time.time())}'
payload = {
    'instanceName': instance_name,
    'qrcode': True,
    'integration': 'WHATSAPP-BAILEYS',
    'token': api_key,
}

url = f'{base_url}/instance/create'
print('='*70)
print('TESTANDO CRIAÇÃO DE INSTÂNCIA E EXTRAÇÃO DE QR CODE')
print('='*70)
print(f'\nURL: {url}')
print(f'Payload: {json.dumps(payload, indent=2)}')

response = requests.post(url, json=payload, headers=headers, timeout=30)

print(f'\nStatus Code: {response.status_code}')
print(f'\nResposta Completa (JSON):\n')

try:
    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    print('\n' + '='*70)
    print('ANÁLISE DA RESPOSTA')
    print('='*70)
    
    # Verificar QR Code
    if 'qrcode' in data:
        print('\n✓ Campo "qrcode" encontrado')
        qr = data['qrcode']
        
        if isinstance(qr, dict):
            print(f'  - Tipo: dict')
            print(f'  - Chaves: {list(qr.keys())}')
            
            if 'base64' in qr:
                print(f'  - base64 presente: {qr["base64"][:50]}...')
            else:
                print(f'  - base64 NÃO presente')
                print(f'  - Conteúdo: {json.dumps(qr, indent=4)[:200]}')
        elif isinstance(qr, str):
            print(f'  - Tipo: string')
            print(f'  - Conteúdo: {qr[:50]}...')
    else:
        print('\n✗ Campo "qrcode" NÃO encontrado na resposta')
    
    # Verificar instance
    if 'instance' in data:
        print('\n✓ Campo "instance" encontrado')
        print(f'  - Chaves: {list(data["instance"].keys())}')
        print(f'  - instanceName: {data["instance"].get("instanceName")}')
        print(f'  - status: {data["instance"].get("status")}')
    
    # Listar todas as chaves
    print('\n✓ Todas as chaves na resposta:')
    for key in data.keys():
        print(f'  - {key}')
    
except Exception as e:
    print(f'Erro ao parsear JSON: {e}')
    print(f'Resposta em texto: {response.text[:500]}')
