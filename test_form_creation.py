#!/usr/bin/env python
"""
Teste completo do fluxo de criação de instância via formulário Django
"""
import os
import sys
import django

# Configurar Django ANTES de qualquer import do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instahunter.settings')
django.setup()

import json
from django.test import Client
from django.contrib.auth.models import User

from instances.models import Instance

def test_instance_creation_via_form():
    """Testa a criação de instância via formulário (como seria via web)"""
    
    # 1. Criar usuário de teste se não existir
    print("\n=== TESTE: Criando instância via formulário ===")
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✓ Usuário criado: {user.username}")
    else:
        print(f"✓ Usuário existente: {user.username}")
    
    # 2. Simular dados do formulário
    form_data = {
        'instance_name': f'test-form-{int(__import__("time").time())}',
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
    
    print(f"\nDados do formulário:")
    for k, v in form_data.items():
        print(f"  {k}: {v}")
    
    # 3. Usar o Client para fazer POST
    client = Client()
    client.force_login(user)
    
    print(f"\nFazendo POST para /instances/criar/...")
    response = client.post('/instances/criar/', data=form_data, follow=True)
    
    print(f"Status Code: {response.status_code}")
    print(f"URL redirecionado para: {response.redirect_chain}")
    
    # 4. Verificar se a instância foi criada
    instance = Instance.objects.filter(instance_name=form_data['instance_name']).first()
    if instance:
        print(f"\n✓ Instância criada com sucesso:")
        print(f"  - ID: {instance.pk}")
        print(f"  - instance_name: {instance.instance_name}")
        print(f"  - instance_id: {instance.instance_id}")
        print(f"  - token: {instance.token}")
        print(f"  - status: {instance.status}")
        print(f"  - qrcode_base64: {'SIM (tamanho: ' + str(len(instance.qrcode_base64)) + ')' if instance.qrcode_base64 else 'NÃO'}")
        
        # 5. Verificar conteúdo da resposta
        print(f"\nConteúdo da página de redirecionamento:")
        print(f"  Status: {response.status_code}")
        if 'qrcode_base64' in response.content.decode():
            print(f"  ✓ QR Code encontrado no HTML da página")
        else:
            print(f"  ⚠ QR Code NÃO encontrado no HTML da página")
    else:
        print(f"\n❌ Instância NÃO foi criada!")
        # Procurar por qualquer instância recente
        recent = Instance.objects.all().order_by('-id')[:3]
        if recent:
            print(f"Instâncias recentes no banco:")
            for inst in recent:
                print(f"  - {inst.instance_name}: status={inst.status}, qrcode={'SIM' if inst.qrcode_base64 else 'NÃO'}")

if __name__ == '__main__':
    test_instance_creation_via_form()
