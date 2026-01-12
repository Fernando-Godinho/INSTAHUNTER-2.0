# Sistema de Distribuição de Tempo para Envio de Mensagens

## 📋 Visão Geral

O sistema de distribuição de tempo foi implementado para permitir o envio de mensagens em massa de forma inteligente, simulando comportamento humano e evitando bloqueios da API do WhatsApp.

## 🎯 Funcionalidades

### 3 Modos de Distribuição

#### 1. **Imediato** (Padrão)
- Envia mensagens com intervalo aleatório entre **1-3 segundos**
- Ideal para: Pequenas quantidades de mensagens (até 50)
- Tempo estimado: ~2 segundos por mensagem

#### 2. **Até Horário Específico**
- Distribui os envios até um horário limite (ex: 17:00)
- Calcula automaticamente o intervalo entre mensagens
- Exemplo: 100 mensagens até às 17h = ~1 mensagem a cada 5 minutos
- Ideal para: Campanhas que precisam terminar em horário específico

#### 3. **Tempo Total (Minutos)**
- Distribui os envios ao longo de um período definido
- Você define quantos minutos quer levar
- Exemplo: 50 mensagens em 60 minutos = ~1 mensagem a cada 1.2 minutos
- Ideal para: Controle preciso do ritmo de envio

## 🔧 Implementação Técnica

### Arquivos Modificados

1. **instances/utils.py** (NOVO)
   - `dividir_tempo_aleatorio()`: Divide tempo total em partes aleatórias
   - `calcular_segundos_ate_horario()`: Calcula segundos até horário alvo
   - `calcular_distribuicao_envio()`: Função principal de distribuição
   - `formatar_tempo()`: Formata segundos em HH:MM:SS

2. **instances/forms.py**
   - Adicionado campo `distribuicao_modo` (ChoiceField)
   - Adicionado campo `hora_limite` (IntegerField 0-23)
   - Adicionado campo `tempo_total_minutos` (IntegerField)

3. **instances/views.py**
   - Importado `calcular_distribuicao_envio`, `formatar_tempo` e `time`
   - Modificado `message_send()` para calcular delays
   - Adicionado `time.sleep()` entre envios
   - Exibe tempo total estimado na mensagem de sucesso

4. **templates/instances/message_send.html**
   - Adicionada seção "Distribuição de Envio"
   - Campos condicionais aparecem baseado no modo selecionado
   - Preview em tempo real da estimativa de envio
   - JavaScript para atualizar preview automaticamente

## 📊 Como Funciona

### Algoritmo de Divisão Aleatória

```python
# Exemplo: Dividir 300 segundos em 5 partes aleatórias
# Resultado: [45, 78, 32, 89, 56] = 300 segundos total
```

O algoritmo:
1. Gera cortes aleatórios no intervalo [0, tempo_total]
2. Ordena os cortes
3. Calcula as diferenças entre cortes consecutivos
4. Aplica correção de arredondamento para garantir precisão

### Exemplo de Uso no Código

```python
# Calcular distribuição para 100 mensagens
delays = calcular_distribuicao_envio(
    num_mensagens=100,
    modo='ate_horario',
    hora_limite=17,  # 17:00
    tempo_total_minutos=None
)

# Resultado: Lista com 100 valores (segundos de espera entre cada envio)
# Ex: [342, 245, 189, 412, ...] (soma = segundos até 17h)
```

## 🎨 Interface do Usuário

### Preview Automático

Quando você:
- Adiciona destinatários
- Seleciona modo de distribuição
- Define horário limite ou tempo total

O sistema mostra automaticamente:
```
✓ 100 mensagens serão distribuídas até às 17:00.
  Tempo disponível: 4h 30min
  Intervalo médio: 3 minutos entre cada envio
```

### Campos Condicionais

- **Modo: Imediato** → Nenhum campo adicional
- **Modo: Até Horário** → Campo "Hora Limite" (0-23)
- **Modo: Tempo Total** → Campo "Tempo Total (minutos)"

## 📈 Exemplos Práticos

### Exemplo 1: Envio Rápido
```
Destinatários: 20
Modo: Imediato
Resultado: 20-60 segundos total
```

### Exemplo 2: Campanha do Dia
```
Destinatários: 500
Modo: Até Horário
Hora Limite: 18 (6pm)
Horário Atual: 10:00am
Resultado: 500 mensagens em 8 horas = ~1 minuto entre cada
```

### Exemplo 3: Distribuição Controlada
```
Destinatários: 100
Modo: Tempo Total
Tempo Total: 120 minutos (2 horas)
Resultado: 100 mensagens em 2 horas = ~1.2 minutos entre cada
```

## ⚙️ Configuração e Validação

### Validação no Formulário

```python
# instances/forms.py
def clean(self):
    modo = self.cleaned_data.get('distribuicao_modo')
    
    # Valida que campos obrigatórios estão presentes
    if modo == 'ate_horario' and not hora_limite:
        raise ValidationError('Hora limite obrigatória')
    
    if modo == 'tempo_total' and not tempo_total_minutos:
        raise ValidationError('Tempo total obrigatório')
```

### Logs no Console

Durante o envio, você verá:
```
Aguardando 45.3s antes do próximo envio... (1/100)
Aguardando 32.1s antes do próximo envio... (2/100)
Aguardando 67.8s antes do próximo envio... (3/100)
...
```

## 🚀 Melhorias Futuras (Opcionais)

1. **Fila Assíncrona com Celery**
   - Envio em background
   - Não bloqueia o navegador
   - Pode agendar para horário futuro

2. **Pausar/Cancelar Envio**
   - Botão para interromper envio em massa
   - Continuar de onde parou

3. **Relatório Detalhado**
   - Mostrar tempo real de envio
   - Gráfico de distribuição temporal
   - Exportar relatório CSV

4. **Personalização de Mensagens**
   - Usar variáveis como {nome}, {empresa}
   - Carregar dados de CSV
   - Template de mensagens

## 🔒 Considerações de Segurança

- ✅ Validação de números de telefone
- ✅ Limite de tamanho de arquivo (16MB)
- ✅ Proteção contra CSRF
- ✅ Sanitização de dados de entrada
- ✅ Rate limiting via distribuição de tempo

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs no console do servidor
2. Teste com poucos destinatários primeiro
3. Ajuste os tempos baseado no comportamento da API
4. Monitore o histórico de mensagens

---

**Última atualização:** Janeiro 2025
**Versão:** 2.0
**Status:** ✅ Pronto para produção
