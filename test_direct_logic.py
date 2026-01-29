#!/usr/bin/env python
"""
Teste direto da lógica de instância_create sem usar Client de teste
"""
import os
import sys
import django

# Configurar Django ANTES de qualquer import do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instahunter.settings')
django.setup()

from instances.models import Instance
from instances.services import EvolutionAPIService
from instances.forms import InstanceForm

def test_create_instance_direct():
    """Testa a criação de instância diretamente com a mesma lógica da view"""
    
    print("\n=== TESTE: Simulando lógica de instance_create ===\n")
    
    # 1. Preparar dados
    instance_name = f'test-direct-{int(__import__("time").time())}'
    form_data = {
        'instance_name': instance_name,
        'number': '5585999999999',
        'integration_type': 'WHATSAPP-BAILEYS',
        'reject_call': False,
        'msg_call': '',
        'groups_ignore': False,
        'always_online': False,
        'read_messages': False,
        'read_status': False,
        'webhook_url': '',
        'webhook_by_events': False,
        'webhook_base64': True,
    }
    
    print(f"1. Criando instância no banco...")
    instance = Instance.objects.create(**form_data)
    print(f"   ✓ Instância criada no banco (ID: {instance.pk})")
    
    # 2. Chamar API (como faz a view)
    print(f"\n2. Chamando api_service.create_instance...")
    api_service = EvolutionAPIService()
    result = api_service.create_instance({
        'instance_name': instance.instance_name,
        'number': instance.number,
        'integration_type': instance.integration_type,
        'qrcode': True,
        'reject_call': instance.reject_call,
        'msg_call': instance.msg_call,
        'groups_ignore': instance.groups_ignore,
        'always_online': instance.always_online,
        'read_messages': instance.read_messages,
        'read_status': instance.read_status,
        'webhook_url': instance.webhook_url,
        'webhook_by_events': instance.webhook_by_events,
        'webhook_base64': instance.webhook_base64,
    })
    
    print(f"   ✓ Resultado recebido. Tipo: {type(result)}")
    print(f"   ✓ Keys: {result.keys() if isinstance(result, dict) else 'N/A'}")
    
    # 3. Processar resultado (como faz a view)
    print(f"\n3. Processando resultado...")
    
    if 'error' in result:
        print(f"   ❌ Erro na API: {result['error']}")
        instance.status = 'error'
        instance.save()
        return
    
    # 4. Extrair dados
    print(f"\n4. Extraindo dados da resposta...")
    instance.instance_id = result.get('instance', {}).get('instanceId') if isinstance(result.get('instance'), dict) else None
    instance.token = result.get('hash') if isinstance(result.get('hash'), str) else None
    print(f"   - instance_id: {instance.instance_id}")
    print(f"   - token: {instance.token}")
    
    # 5. Extrair QR Code
    print(f"\n5. Extraindo QR Code...")
    qrcode_saved = False
    
    if isinstance(result, dict) and 'qrcode' in result:
        print(f"   ✓ 'qrcode' encontrado em result")
        if isinstance(result['qrcode'], dict) and 'base64' in result['qrcode']:
            instance.qrcode_base64 = result['qrcode']['base64']
            qrcode_saved = True
            instance.status = 'connecting'
            print(f"   ✓ QR Code extraído (formato 1). Tamanho: {len(instance.qrcode_base64)}")
        elif isinstance(result['qrcode'], str):
            instance.qrcode_base64 = result['qrcode']
            qrcode_saved = True
            instance.status = 'connecting'
            print(f"   ✓ QR Code extraído (formato 2). Tamanho: {len(instance.qrcode_base64)}")
    else:
        print(f"   ❌ 'qrcode' NÃO encontrado em result")
    
    # 6. Salvar
    if not qrcode_saved:
        instance.status = 'created'
    
    instance.save()
    
    # 7. Verificar resultado
    print(f"\n6. Resultado final...")
    instance_updated = Instance.objects.get(pk=instance.pk)
    print(f"   - instance_name: {instance_updated.instance_name}")
    print(f"   - instance_id: {instance_updated.instance_id}")
    print(f"   - token: {instance_updated.token}")
    print(f"   - status: {instance_updated.status}")
    print(f"   - qrcode_base64: {'SIM' if instance_updated.qrcode_base64 else 'NÃO'}")
    
    if instance_updated.qrcode_base64:
        print(f"   ✓ QR Code tamanho: {len(instance_updated.qrcode_base64)}")
        print(f"   ✓ QR Code começa com: {instance_updated.qrcode_base64[:50]}...")
    
    return instance_updated

if __name__ == '__main__':
    test_create_instance_direct()
