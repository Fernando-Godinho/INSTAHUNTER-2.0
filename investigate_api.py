#!/usr/bin/env python
"""
Script para investigar endpoints da Evolution API
"""
import os
import sys
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instahunter.settings')
django.setup()

from django.conf import settings

base_url = settings.EVOLUTION_API_URL
api_key = settings.EVOLUTION_API_KEY
headers = {'apikey': api_key, 'Content-Type': 'application/json'}

instance_name = 'RHINO'

print('='*70)
print('INVESTIGANDO ENDPOINT /instance/connect')
print('='*70)

url = f'{base_url}/instance/connect/{instance_name}'

print(f'\n[GET] /instance/connect/{instance_name}')
response = requests.get(url, headers=headers, timeout=5)
print(f'Status: {response.status_code}')
print(f'Response: {response.text}')

print('\n[GET] /instance/connect/NAOEXISTE123')
url = f'{base_url}/instance/connect/NAOEXISTE123'
response = requests.get(url, headers=headers, timeout=5)
print(f'Status: {response.status_code}')
if response.status_code != 200:
    print(f'Response: {response.text[:300]}')

print('\n' + '='*70)
print('COMPARANDO ENDPOINTS')
print('='*70)

tests = [
    ('GET /instance/connect/{name}', requests.get, f'{base_url}/instance/connect/{instance_name}'),
    ('POST /instance/restart/{name}', requests.post, f'{base_url}/instance/restart/{instance_name}'),
    ('GET /instance/connectionState/{name}', requests.get, f'{base_url}/instance/connectionState/{instance_name}'),
]

for desc, method, url in tests:
    print(f'\n{desc}')
    try:
        if method == requests.get:
            response = method(url, headers=headers, timeout=5)
        else:
            response = method(url, json={}, headers=headers, timeout=5)
        
        print(f'  Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'  Data: {json.dumps(data, indent=2)[:200]}')
    except Exception as e:
        print(f'  Error: {e}')
