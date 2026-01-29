#!/usr/bin/env python
"""
Força a geração e salvamento do QR Code para a instância 11
"""
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instahunter.settings')
django.setup()

from instances.models import Instance
from instances.services import EvolutionAPIService

inst = Instance.objects.get(pk=11)
print(f"Gerando QR Code para: {inst.instance_name}")

api_service = EvolutionAPIService()

# Opção 1: Tentar com connect_instance (GET)
print("\n1️⃣ Tentando com connect_instance (GET)...")
result = api_service.connect_instance(inst.instance_name)
print(f"Resultado: {json.dumps(result, indent=2)[:200]}...")

if 'error' not in result:
    print("✓ Sucesso!")
    # Salvar QR Code se encontrado
    if 'base64' in result:
        inst.qrcode_base64 = result['base64']
        inst.status = 'connecting'  # ou 'open' se estiver conectado
        inst.save()
        print(f"✓ QR Code salvo! Tamanho: {len(inst.qrcode_base64)}")
        print(f"✓ Status atualizado: {inst.status}")
    elif 'instance' in result and 'state' in result['instance']:
        inst.status = result['instance']['state']
        inst.save()
        print(f"✓ Status atualizado: {inst.status}")
else:
    print(f"❌ Erro: {result['error']}")
    
    # Opção 2: Tentar reiniciar a instância
    print("\n2️⃣ Tentando reiniciar a instância...")
    restart_result = api_service.restart_instance(inst.instance_name)
    print(f"Resultado com keys: {restart_result.keys() if isinstance(restart_result, dict) else 'N/A'}")
    
    if 'error' not in restart_result and 'qrcode' in restart_result:
        if 'base64' in restart_result['qrcode']:
            inst.qrcode_base64 = restart_result['qrcode']['base64']
            inst.status = 'connecting'
            inst.save()
            print(f"✓ QR Code salvo! Tamanho: {len(inst.qrcode_base64)}")
            print(f"✓ Status atualizado: {inst.status}")

