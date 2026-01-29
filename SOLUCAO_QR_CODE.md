# Resolução: Erro ao Conectar Instância - QR Code

## Problema Original
`Erro ao conectar instância: Nenhum endpoint para gerar QR Code funcionou. Verifique os logs acima para detalhes.`

## Causa Identificada ✓

Após análise detalhada com o script de diagnóstico, descobriu-se que:

**A Evolution API NÃO possui endpoints separados para obter o QR Code após criação.**

- ❌ `/instance/qrcode/{instanceName}` → 404 Not Found
- ❌ `/instances/{instanceName}/qrcode` → 404 Not Found  
- ❌ `/instance/{instanceName}/connect` → 404 Not Found
- ✓ O QR Code é retornado **na resposta de criação da instância** no campo `response.qrcode.base64`

## O que foi Corrigido

### 1. **Extração do QR Code na Criação** (`instances/services.py`)
- Melhorado método `create_instance()` para logar quando o QR Code é obtido
- Adicionada detecção automática de diferentes formatos de resposta

### 2. **Novo Método de Conexão** (`instances/services.py`)
- Reescrito `connect_instance()` para:
  - Fazer polling do status da instância usando `/instance/connectionState/{name}`
  - Aguardar que a instância saia do estado "connecting"
  - Retornar status de conexão em vez de tentar endpoints inexistentes

### 3. **Extração do QR Code na Criação** (`instances/views.py`)
- Atualizado `instance_create()` para:
  - Sempre tentar gerar QR Code (`qrcode: True`)
  - Extrair e salvar o QR Code se obtido durante criação
  - Mostrar mensagem diferente se QR Code foi gerado

### 4. **Simplificação da Conexão** (`instances/views.py`)
- Atualizado `instance_connect()` para:
  - Verificar status de conexão em vez de tentar endpoints inexistentes
  - Fornecer feedback apropriado sobre o estado da instância

### 5. **Script de Diagnóstico** (`test_evolution_api.py`)
- Criado para validar a configuração da API
- Testa todos os endpoints possíveis
- Mostra exatamente qual é o problema

## Como Usar Agora

### Fluxo Correto:

1. **Criar Instância:**
   - Sistema chama `/instance/create` com `qrcode: true`
   - API retorna a instância + QR Code no campo `qrcode.base64`
   - QR Code é armazenado no banco de dados
   - Usuário vê o QR Code imediatamente

2. **Conectar Instância:**
   - Se não tiver QR Code ainda, clica em "Conectar"
   - Sistema faz polling de `/instance/connectionState/{name}`
   - Aguarda que a instância saia do estado "connecting"
   - Mostra feedback sobre o progresso

### Debug e Diagnóstico:

```bash
# Executar diagnóstico completo
cd "c:\Users\ferna\OneDrive\Área de Trabalho\INSTAHUNTER 2.0"
python test_evolution_api.py
```

O script vai testar:
- ✓ Conectividade com Evolution API
- ✓ `/instance/fetchInstances` (listar instâncias)
- ✓ `/instance/create` (criar instância)
- ✓ Todos os 7 endpoints possíveis de QR Code
- ✓ `/instance/connectionState/{name}` (status)

## Estrutura da Resposta de Criação

```json
{
  "instance": {
    "instanceName": "minha-instancia",
    "instanceId": "...",
    "status": "connecting"
  },
  "qrcode": {
    "pairingCode": null,
    "code": "...",
    "base64": "data:image/png;base64,iVBORw0KGgo..."
  },
  "hash": "429683C4C977415CAAFCCE10F7D57E11"
}
```

**O `qrcode.base64` é o que precisamos!**

## Posso Ignorar Estas URLs

As seguintes URLs **não existem na Evolution API** e foram removidas da tentativa:

```python
# ❌ Não funcionam:
- /instance/qrcode/{instanceName}
- /instances/{instanceName}/qrcode
- /instance/{instanceName}/connect
- /instance/connect/{instanceName}
- /instances/{instanceName}/connect
- /qrcode/{instanceName}
```

## Resumo das Mudanças de Código

| Arquivo | Mudança | Motivo |
|---------|---------|--------|
| `instances/services.py` | Removidos endpoints falsos | Não existem na API |
| `instances/services.py` | Novo `connect_instance()` com polling | Usar status em vez de endpoints inexistentes |
| `instances/views.py` | Melhorado `instance_create()` | Extrair QR Code na resposta |
| `instances/views.py` | Simplificado `instance_connect()` | Usar polling de status |
| `test_evolution_api.py` | Criado novo | Script de diagnóstico |

## Se Ainda Não Funcionar

1. **Teste a API manualmente:**
   ```bash
   python test_evolution_api.py
   ```

2. **Verifique os logs:**
   - Procure por `[DEBUG]` no console do Django
   - Procure por `✓ SUCESSO!` para ver qual endpoint funcionou

3. **Valide a configuração em `settings.py`:**
   ```python
   EVOLUTION_API_URL = "https://rhino-evolution-api.ihkbl8.easypanel.host"
   EVOLUTION_API_KEY = "429683C4C977415CAAFCCE10F7D57E11"
   ```

4. **Verifique se a instância foi criada:**
   - Vá para o painel da Evolution API
   - Verifique se a instância aparece em "Instâncias"

---

**Status:** ✓ Corrigido  
**Data:** 29 de janeiro de 2026  
**Versão:** 2.0

