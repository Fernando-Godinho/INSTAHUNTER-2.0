#!/usr/bin/env python
"""
Teste completo do fluxo de criação de instância
"""
import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instahunter.settings')
django.setup()

from instances.models import Instance
from instances.services import EvolutionAPIService

def test_create_and_extract():
    """Testa a criação de instância e extração de QR Code"""
    api_service = EvolutionAPIService()
    
    # 1. Criar instância na API
    print("\n=== TESTE 1: Criando instância na API ===")
    instance_data = {
        'instance_name': f'test-full-flow-{int(__import__("time").time())}',
        'number': '5585999999999',  # Número genérico para teste
        'integration_type': 'WHATSAPP-BAILEYS',
        'qrcode': True,
    }
    
    result = api_service.create_instance(instance_data)
    
    print(f"\nResposta da API:")
    print(json.dumps(result, indent=2))
    
    # 2. Analisar resposta
    print("\n=== TESTE 2: Analisando resposta ===")
    
    if 'error' in result:
        print(f"❌ ERRO: {result['error']}")
        return
    
    # Checar se tem QR Code
    has_qrcode = False
    qrcode_value = None
    
    if 'qrcode' in result:
        print(f"✓ Campo 'qrcode' encontrado")
        if isinstance(result['qrcode'], dict):
            print(f"  - Tipo: dict")
            if 'base64' in result['qrcode']:
                has_qrcode = True
                qrcode_value = result['qrcode']['base64']
                print(f"  - QR Code base64 encontrado: {len(qrcode_value)} chars")
        elif isinstance(result['qrcode'], str):
            print(f"  - Tipo: string")
            has_qrcode = True
            qrcode_value = result['qrcode']
            print(f"  - QR Code encontrado: {len(qrcode_value)} chars")
    else:
        print(f"❌ Campo 'qrcode' NÃO encontrado")
    
    # 3. Simular salvamento no banco de dados
    print("\n=== TESTE 3: Salvando no banco de dados ===")
    
    try:
        instance = Instance.objects.create(
            instance_name=instance_data['instance_name'],
            number=instance_data['number'],
            integration_type=instance_data['integration_type'],
            instance_id=result.get('instance', {}).get('instanceId'),
            token=result.get('hash'),
            qrcode_base64=qrcode_value if has_qrcode else None,
            status='connecting' if has_qrcode else 'created'
        )
        print(f"✓ Instância salva no banco de dados (ID: {instance.pk})")
        print(f"  - instance_name: {instance.instance_name}")
        print(f"  - qrcode_base64: {'SIM' if instance.qrcode_base64 else 'NÃO'}")
        print(f"  - status: {instance.status}")
        
        # 4. Verificar estado da instância
        print("\n=== TESTE 4: Verificando estado na API ===")
        status = api_service.get_instance_status(instance.instance_name)
        print(f"Status API: {json.dumps(status, indent=2)}")
        
    except Exception as e:
        print(f"❌ ERRO ao salvar: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_create_and_extract()
