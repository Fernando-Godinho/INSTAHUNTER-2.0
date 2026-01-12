# 🎯 Guia Rápido - Distribuição de Tempo

## Como Usar

### 1️⃣ Acesse o Formulário de Envio
- Menu: **"Enviar Mensagens"**
- Preencha os campos básicos:
  - ✅ Instância
  - ✅ Destinatários (um por linha)
  - ✅ Tipo de mensagem
  - ✅ Conteúdo/Arquivo

### 2️⃣ Configure a Distribuição

#### 🚀 MODO: Imediato (Padrão)
```
[x] Imediato
    └─ Intervalo: 1-3 segundos aleatório
    └─ Melhor para: Até 50 mensagens
```

#### ⏰ MODO: Até Horário
```
[x] Até Horário Específico
    └─ Hora Limite: [17] (5pm)
    └─ Sistema calcula automaticamente os intervalos
    └─ Melhor para: Campanhas com deadline
```

#### ⏱️ MODO: Tempo Total
```
[x] Tempo Total (minutos)
    └─ Tempo Total: [60] minutos
    └─ Distribui igualmente ao longo do período
    └─ Melhor para: Controle preciso do ritmo
```

### 3️⃣ Veja o Preview

O sistema mostra automaticamente:

```
┌──────────────────────────────────────────┐
│ ⓘ Estimativa de envio:                   │
│                                           │
│ 100 mensagens serão distribuídas         │
│ até às 17:00.                            │
│                                           │
│ ⏱️ Tempo disponível: 4h 30min            │
│ 📊 Intervalo médio: 3 minutos/envio     │
└──────────────────────────────────────────┘
```

### 4️⃣ Envie as Mensagens

Clique em **"Enviar Mensagem"** e aguarde.

Durante o envio:
- ✅ Progresso no console do servidor
- ✅ Mensagem de sucesso com tempo total
- ✅ Histórico salvo automaticamente

---

## 💡 Dicas Práticas

### ✅ FAÇA:
- Teste com poucos números primeiro
- Use "Imediato" para testes rápidos
- Use "Até Horário" para campanhas agendadas
- Monitore o histórico de mensagens

### ❌ NÃO FAÇA:
- Enviar centenas sem testar antes
- Usar tempo total muito curto (risco de bloqueio)
- Fechar o navegador durante envio em massa
- Usar a mesma mensagem para todos (personalize!)

---

## 🎓 Casos de Uso

### 📣 Marketing de Produto
```
Destinatários: 200 clientes
Modo: Até Horário (18:00)
Resultado: Todos recebem até o fim do dia útil
```

### 🎉 Convite para Evento
```
Destinatários: 50 convidados
Modo: Imediato
Resultado: Todos recebem em 2-3 minutos
```

### 📢 Newsletter Semanal
```
Destinatários: 500 assinantes
Modo: Tempo Total (180 minutos)
Resultado: Distribuído ao longo de 3 horas
```

### 🔔 Lembrete Urgente
```
Destinatários: 30 pessoas
Modo: Imediato
Resultado: Envio instantâneo
```

---

## 📊 Comparação dos Modos

| Modo | Velocidade | Controle | Melhor Para |
|------|------------|----------|-------------|
| **Imediato** | ⚡⚡⚡ | ⭐ | Mensagens urgentes |
| **Até Horário** | ⚡⚡ | ⭐⭐⭐ | Campanhas agendadas |
| **Tempo Total** | ⚡ | ⭐⭐⭐ | Distribuição uniforme |

---

## 🆘 Solução de Problemas

### "Mensagem não enviada"
- ✅ Verifique se a instância está conectada
- ✅ Valide o número do destinatário (+5511999999999)
- ✅ Teste com um número primeiro

### "Muito lento"
- ✅ Use modo "Imediato" para envios rápidos
- ✅ Reduza o tempo total
- ✅ Reduza o número de destinatários

### "API bloqueou"
- ❌ Você enviou rápido demais
- ✅ Aumente os intervalos
- ✅ Use distribuição mais espaçada
- ✅ Aguarde alguns minutos antes de tentar novamente

---

## 📈 Estatísticas de Referência

### Limites Seguros (Estimados)

| Período | Mensagens Seguras | Modo Recomendado |
|---------|-------------------|------------------|
| 1 hora | 60-100 | Tempo Total (60min) |
| 4 horas | 200-300 | Até Horário |
| 1 dia | 500-1000 | Até Horário (17h) |

> ⚠️ **Nota:** Estes são valores de referência. Ajuste baseado no comportamento da sua API.

---

**🎯 Pronto para usar!** 
Abra o sistema e teste com alguns números primeiro.
