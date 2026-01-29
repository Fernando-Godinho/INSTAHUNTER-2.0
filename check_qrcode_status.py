#!/usr/bin/env python
"""
RESUMO FINAL: Estado do QR Code e Solução
==========================================

✅ CONFIRMADO: API está funcionando e retornando QR Code corretamente
✅ CONFIRMADO: Lógica de extração está correta
⏳ PROBLEMA: Algo está falhando quando criar via interface web

PRÓXIMOS PASSOS:
1. Execute os testes abaixo para validar seu ambiente
2. Crie uma instância via web e procure pelos logs [instance_create]
3. Cole os logs aqui para debug final

TESTES DISPONÍVEIS:
- test_full_flow.py: Testa API + criação no banco
- test_direct_logic.py: Testa a lógica da view
- test_form_creation.py: Testa via formulário Django
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instahunter.settings')
django.setup()

from instances.models import Instance

def show_summary():
    """Mostra resumo do estado das instâncias"""
    
    print("\n" + "="*70)
    print("RESUMO: INSTÂNCIAS NO BANCO DE DADOS")
    print("="*70)
    
    # Pegar todas as instâncias primeiro
    all_instances = Instance.objects.all().order_by('-id')
    instances = all_instances[:10]
    
    if not instances:
        print("Nenhuma instância encontrada!")
        return
    
    print(f"\n{'ID':<5} {'Nome':<30} {'Status':<12} {'QR Code':<10} {'Instance ID':<8}")
    print("-"*70)
    
    for inst in instances:
        has_qr = "SIM" if inst.qrcode_base64 else "NÃO"
        print(f"{inst.pk:<5} {inst.instance_name[:29]:<30} {inst.status:<12} {has_qr:<10} {str(inst.instance_id)[:7]:<8}")
    
    # Análise
    print("\n" + "="*70)
    print("ANÁLISE")
    print("="*70)
    
    total = all_instances.count()
    with_qr = all_instances.exclude(qrcode_base64='').exclude(qrcode_base64__isnull=True).count()
    without_qr = total - with_qr
    
    print(f"Total de instâncias: {total}")
    print(f"Com QR Code: {with_qr}")
    print(f"Sem QR Code: {without_qr}")
    
    if without_qr > 0:
        print(f"\n⚠️  {without_qr} instância(s) SEM QR Code:")
        for inst in all_instances.filter(qrcode_base64__isnull=True) | all_instances.filter(qrcode_base64=''):
            print(f"  - {inst.instance_name} (status: {inst.status})")
    
    print("\n" + "="*70)
    print("PRÓXIMOS PASSOS")
    print("="*70)
    print("""
1. ✅ VERIFICADO: API está retornando QR Code corretamente
2. ✅ VERIFICADO: Lógica de extração está correta
3. ⏳ NECESSÁRIO: Testar criação via interface web

Para criar uma instância com DEBUG:
1. Inicie o servidor: python manage.py runserver
2. Vá para: http://localhost:8000/instances/criar/
3. Preencha o formulário e clique em enviar
4. Procure pelos logs [instance_create] no console
5. Verifique se o status foi 'connecting' ou 'created'
6. Crie uma issue com os logs se tiver erro

Logs esperados:
  [instance_create] Chamando api_service.create_instance...
  [instance_create] Resultado recebido...
  [instance_create] Tentando extrair QR Code...
  [instance_create] ✓ QR Code extraído...
  [instance_create] Instância salva...
""")

if __name__ == '__main__':
    show_summary()
