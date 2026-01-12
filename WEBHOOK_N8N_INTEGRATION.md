# Integração com Webhook N8N

## Resumo das Mudanças

Este documento descreve as mudanças realizadas para integrar o aplicativo com o webhook do n8n (https://n8n.sumconnectia.tech/webhook/activeSender).

### Alterações Realizadas:

#### 1. **Arquivo: `instances/services.py`**
- ✅ Adicionado novo método `send_to_n8n_webhook()` na classe `EvolutionAPIService`
- O método envia dados de contatos e arquivos para o webhook do n8n
- Formato de payload conforme especificado:
  ```json
  {
    "id_instancia": "123",
    "contatos": [
      {
        "Telefone": "5511999999999",
        "Mensagem": "Texto da mensagem"
      }
    ],
    "arquivo_para_envio": {
      "nome": "nome_arquivo.png",
      "tipo": "image/png",
      "tamanho": 12345,
      "base64": "iVBORw0KGgoAAAANS..."
    }
  }
  ```

#### 2. **Arquivo: `instances/forms.py`**
- ✅ Removidos campos de distribuição de tempo de `SendMessageForm`:
  - `distribuicao_modo`
  - `hora_limite`
  - `tempo_total_minutos`
- ✅ Removidos campos de distribuição de tempo de `BulkMessageForm`:
  - `distribuicao_modo`
  - `hora_limite`
  - `tempo_total_minutos`

#### 3. **Arquivo: `instances/views.py`**
- ✅ Removidas importações não mais necessárias:
  - `calcular_distribuicao_envio` 
  - `formatar_tempo`
  - `time`
- ✅ Atualizada função `message_send()`:
  - Removida lógica de cálculo de distribuição de tempo
  - Removidos delays de envio
  - Adicionada preparação de dados para webhook do n8n
  - Adicionada chamada ao novo método `send_to_n8n_webhook()`
  - Arquivo convertido para base64 e incluído no payload
- ✅ Atualizada função `message_bulk()`:
  - Mesmo as mudanças da função `message_send()`
  - Agora envia dados para webhook em vez de enviar direto pela Evolution API

### Fluxo de Envio Novo:

1. Usuário preenche formulário com:
   - Instância (WhatsApp)
   - Números dos destinatários
   - Tipo de mensagem (texto ou mídia)
   - Conteúdo (mensagem ou arquivo)

2. Aplicativo processa os dados:
   - Agrupa destinatários em formato de contatos
   - Se houver arquivo, converte para base64
   - Prepara payload JSON

3. Envia para webhook N8N:
   ```
   POST https://n8n.sumconnectia.tech/webhook/activeSender
   ```

4. O n8n recebe e processa o envio (distribuição, delays, etc.)

### Benefícios:

- ✅ Lógica de distribuição de tempo centralizada no n8n
- ✅ Aplicativo mais leve e responsivo
- ✅ Fácil manutenção e atualização de regras de envio
- ✅ Escalabilidade melhorada

### Testes:

O servidor foi testado e iniciado com sucesso na porta 8001:
```
python manage.py runserver 0.0.0.0:8001
```

Nenhum erro de sintaxe ou importação foi detectado.

### Próximos Passos (Opcional):

1. Remover campos de distribuição dos templates HTML
2. Remover imports do arquivo `utils.py` (se não for mais utilizado)
3. Atualizar documentação de uso do aplicativo

---

**Data:** 12 de Janeiro de 2026  
**Status:** Implementação Concluída ✅
