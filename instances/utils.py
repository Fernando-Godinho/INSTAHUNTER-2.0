"""
Utilitários para o app instances
"""
import random
from datetime import datetime, time as dt_time
from typing import List


def dividir_tempo_aleatorio(total_segundos: float, partes: int) -> List[float]:
    """
    Divide um tempo total em partes aleatórias.
    
    Args:
        total_segundos: Tempo total em segundos a ser dividido
        partes: Número de partes para dividir
    
    Returns:
        Lista com os tempos de espera em segundos para cada parte
    """
    if partes <= 0:
        return []
    
    if partes == 1:
        return [total_segundos]
    
    # Gerar cortes aleatórios
    cortes = [random.random() * total_segundos for _ in range(partes - 1)]
    cortes.sort()
    cortes = [0] + cortes + [total_segundos]
    
    # Calcular diferenças entre cortes
    resultado = []
    for i in range(partes):
        diff = cortes[i + 1] - cortes[i]
        resultado.append(round(diff, 4))
    
    # Corrigir diferença de arredondamento
    soma = sum(resultado)
    diferenca = total_segundos - soma
    resultado[0] = round(resultado[0] + diferenca, 4)
    
    return resultado


def calcular_segundos_ate_horario(hora_limite: int = 17, minuto_limite: int = 0) -> float:
    """
    Calcula quantos segundos faltam até um horário específico hoje.
    
    Args:
        hora_limite: Hora do horário limite (0-23)
        minuto_limite: Minuto do horário limite (0-59)
    
    Returns:
        Segundos até o horário limite. Retorna 0 se já passou.
    """
    agora = datetime.now()
    hora_atual_segundos = agora.hour * 3600 + agora.minute * 60 + agora.second
    limite_segundos = hora_limite * 3600 + minuto_limite * 60
    
    return max(0, limite_segundos - hora_atual_segundos)


def formatar_tempo(segundos: float) -> str:
    """
    Formata segundos em formato legível (HH:MM:SS).
    
    Args:
        segundos: Tempo em segundos
    
    Returns:
        String formatada
    """
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segs = int(segundos % 60)
    
    if horas > 0:
        return f"{horas}h {minutos}m {segs}s"
    elif minutos > 0:
        return f"{minutos}m {segs}s"
    else:
        return f"{segs}s"


def calcular_distribuicao_envio(quantidade_mensagens: int, modo: str = 'imediato', 
                                hora_limite: int = None, tempo_total: int = None) -> List[float]:
    """
    Calcula a distribuição de tempo entre mensagens.
    
    Args:
        quantidade_mensagens: Número de mensagens a enviar
        modo: 'imediato', 'ate_horario', ou 'tempo_total'
        hora_limite: Hora limite para modo 'ate_horario' (formato 24h)
        tempo_total: Tempo total em minutos para modo 'tempo_total'
    
    Returns:
        Lista com os tempos de espera antes de cada envio
    """
    if quantidade_mensagens <= 0:
        return []
    
    if modo == 'imediato':
        # Envio imediato com intervalo mínimo de 1-3 segundos entre mensagens
        return [random.uniform(1, 3) for _ in range(quantidade_mensagens)]
    
    elif modo == 'ate_horario' and hora_limite is not None:
        # Distribuir até um horário específico
        segundos_disponiveis = calcular_segundos_ate_horario(hora_limite)
        
        if segundos_disponiveis <= 0:
            # Se já passou do horário, usar modo imediato
            return [random.uniform(1, 3) for _ in range(quantidade_mensagens)]
        
        return dividir_tempo_aleatorio(segundos_disponiveis, quantidade_mensagens)
    
    elif modo == 'tempo_total' and tempo_total is not None:
        # Distribuir em um tempo total específico (em minutos)
        segundos_disponiveis = tempo_total * 60
        return dividir_tempo_aleatorio(segundos_disponiveis, quantidade_mensagens)
    
    # Fallback para modo imediato
    return [random.uniform(1, 3) for _ in range(quantidade_mensagens)]
