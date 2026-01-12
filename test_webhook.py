"""
Exemplo de teste para a integração com webhook n8n
Execute este arquivo para testar a função send_to_n8n_webhook
"""

import os
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instahunter.settings')
django.setup()

from instances.services import EvolutionAPIService

def test_webhook_integration():
    """
    Testa a integração com webhook n8n
    """
    api_service = EvolutionAPIService()
    
    # Dados de teste
    contatos = [
        {
            "Telefone": "5551996210443",
            "Mensagem": "Oi! Tudo certo? Aqui é o Fernando, de Sapucaia do Sul – RS 👋\nMe conta rapidinho como funciona o fluxo de vocês? Consigo ver onde a automação pode facilitar bastante.\nSe quiser testar, automatizo uma planilha grátis pra você — só mandar AUTO."
        },
        {
            "Telefone": "5551999088761",
            "Mensagem": "Oi! Tudo certo? Aqui é o Fernando, de Sapucaia do Sul – RS 👋\nMe conta rapidinho como funciona o fluxo de vocês? Consigo ver onde a automação pode facilitar bastante.\nSe quiser testar, automatizo uma planilha grátis pra você — só mandar AUTO."
        }
    ]
    
    print("=" * 60)
    print("TESTANDO INTEGRAÇÃO COM WEBHOOK N8N")
    print("=" * 60)
    print()
    
    print(f"Enviando {len(contatos)} contatos para webhook...")
    print()
    
    result = api_service.send_to_n8n_webhook(
        instance_id="537",
        contatos=contatos
    )
    
    print()
    print("=" * 60)
    print("RESULTADO:")
    print("=" * 60)
    print(result)
    print()
    
    if 'error' in result:
        print("❌ Erro ao enviar para webhook!")
        print(f"Mensagem: {result['error']}")
    else:
        print("✅ Webhook enviado com sucesso!")
        print("Resposta do n8n:")
        for key, value in result.items():
            print(f"  {key}: {value}")

if __name__ == '__main__':
    try:
        test_webhook_integration()
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
