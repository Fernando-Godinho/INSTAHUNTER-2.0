# Solução: QR Code não está sendo Gerado/Salvo na Criação de Instância

## Problema Identificado
Usuário reportou: "Estado da instância: unknown mas n gerou o qrcode"

## Análise Realizada

### 1. API (Evolution API) - ✅ FUNCIONANDO
- Endpoint: `POST /instance/create`
- Retorna: Status 201 com resposta completa incluindo `qrcode.base64`
- Confirmado com `test_full_flow.py`: API retorna dados corretos

### 2. Serviço (instances/services.py) - ✅ FUNCIONANDO  
- Método `create_instance()` retorna a resposta completa do JSON
- Método `connect_instance()` retorna o estado corretamente
- Debug mostra: QR Code obtido na criação ✓

### 3. View (instances/views.py) - ✅ CÓDIGO CORRETO
- Extrair QR Code da resposta: `result['qrcode']['base64']` ✓
- Salvar em banco de dados: `instance.save()` ✓
- Lógica testada com `test_direct_logic.py`: Funciona corretamente

## Resultado dos Testes

### test_full_flow.py
```
✓ Instância criada no banco (ID: 12)
✓ QR Code extraído na criação (formato 1)
✓ QR Code tamanho: 13478 chars
✓ Status: connecting
```

### test_direct_logic.py  
```
✓ Instância criada no banco (ID: 13)
✓ QR Code extraído (formato 1). Tamanho: 13414
✓ Status: connecting
✓ QR Code começa com: data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAVwA...
```

## Causa Raiz Identificada

A instância "teste qua qua" que você criou tem:
- `status = 'unknown'`
- `qrcode_base64 = NULL` (vazio)

Isso indica que quando foi criada via interface web, algo falhou entre a criação da instância no banco e a chamada da API.

Possíveis causas:
1. **Timeout na requisição da API** - A conexão com Evolution API timeout após salvar no banco
2. **Erro não capturado** - Exceção que não foi capturada corretamente
3. **Número inválido** - Campo 'number' vazio ou com formato incorreto

## Solução Aplicada

Adicionei **logging detalhado** na view `instance_create()` para debugar o exato ponto de falha:

**Arquivo**: `instances/views.py` (linhas 45-120)

```python
print(f"[instance_create] Chamando api_service.create_instance com dados: {instance_data}")
result = api_service.create_instance(instance_data)
print(f"[instance_create] Resultado recebido: {result}")
print(f"[instance_create] Tentando extrair QR Code. result keys: {result.keys()}")
# ... logs adicionais
print(f"[instance_create] Salvando instância. qrcode_saved: {qrcode_saved}, status: {instance.status}")
instance.save()
print(f"[instance_create] Instância salva. ID: {instance.pk}")
```

## Próximas Etapas

1. **Testar a criação via web** e procurar pelos logs `[instance_create]` no console Django
2. **Verificar o arquivo de log** se estiver configurado
3. **Analisar o erro específico** que está impedindo a criação

## Como Usar os Testes

### Teste da API diretamente:
```bash
python test_full_flow.py
```

### Teste da lógica da view:
```bash
python test_direct_logic.py
```

### Teste via interface web:
1. Inicie o servidor: `python manage.py runserver`
2. Acesse: http://localhost:8000/instances/criar/
3. Preencha o formulário
4. Observe os logs `[instance_create]` no console
5. Verifique se QR Code foi salvo no banco

## Status
- ✅ API funcionando corretamente
- ✅ Lógica de extração correta
- ✅ Logs adicionados para debug
- ⏳ Aguardando teste via web para identificar o erro exato
