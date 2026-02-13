import requests
import json

# URL local (ajuste se estiver rodando em outra porta)
url = "http://localhost:8000/webhook/waba/"

# JSON enviado pelo usuário
payload = [
  {
    "body": {
      "object": "whatsapp_business_account",
      "entry": [
        {
          "id": "916791347543446",
          "changes": [
            {
              "value": {
                "messaging_product": "whatsapp",
                "metadata": {
                  "display_phone_number": "551153330101",
                  "phone_number_id": "942971575572951"
                },
                "contacts": [
                  {
                    "profile": {
                      "name": "Fernando Godinho"
                    },
                    "wa_id": "555183097389"
                  }
                ],
                "messages": [
                  {
                    "from": "555183097389",
                    "id": "wamid.HBgMNTU1MTgzMDk3Mzg5FQIAEhgWM0VCMDY5RDE0RDBEODM1RTlEODlDMAA=" + str(json.dumps(True)), # UUID fake
                    "timestamp": "1770996135",
                    "text": {
                      "body": "Teste de Mensagem Recebida via Webhook!"
                    },
                    "type": "text"
                  }
                ]
              },
              "field": "messages"
            }
          ]
        }
      ]
    }
  }
]

headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Erro: {str(e)}")
