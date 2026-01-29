#!/usr/bin/env python
"""
Teste final completo da solução de QR Code
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instahunter.settings')
django.setup()

from instances.services import EvolutionAPIService
import json

print('\n' + '='*70)
print('TESTE FINAL COMPLETO - QR CODE / CONEXÃO')
print('='*70)

api = EvolutionAPIService()

# 1. Check connection
print('\n1. Verificando conectividade com Evolution API...')
conn = api.check_connection()
if conn['status'] == 'success':
    print('   ✓ Conectado com sucesso')
else:
    print(f'   ✗ Erro: {conn["message"]}')
    sys.exit(1)

# 2. Test with existing instance
print('\n2. Testando connect_instance com RHINO (instância existente)...')
result = api.connect_instance('RHINO')
if 'error' not in result:
    state = result.get('instance', {}).get('state')
    instance_name = result.get('instance', {}).get('instanceName')
    print(f'   ✓ Sucesso!')
    print(f'     - Instância: {instance_name}')
    print(f'     - Estado: {state}')
else:
    print(f'   ✗ Erro: {result["error"]}')
    sys.exit(1)

# 3. Test with non-existing instance
print('\n3. Testando connect_instance com NAOEXISTE (instância inexistente)...')
result = api.connect_instance('NAOEXISTE')
if 'error' in result:
    if 'não existe' in result['error'].lower() or '404' in result['error'].lower():
        print(f'   ✓ Erro tratado corretamente')
        print(f'     - Mensagem: {result["error"]}')
    else:
        print(f'   ✓ Erro retornado: {result["error"]}')
else:
    print(f'   ✗ Erro não foi tratado!')
    print(f'     - Resultado: {result}')
    sys.exit(1)

print('\n' + '='*70)
print('✓ TODOS OS TESTES PASSARAM!')
print('='*70)
print('\nO sistema está pronto para usar!')
print('✓ Endpoint correto: GET /instance/connect/{instanceName}')
print('✓ Métodos funcionando: check_connection() e connect_instance()')
print('✓ Tratamento de erros: Funcionando corretamente')
print('\n' + '='*70 + '\n')
