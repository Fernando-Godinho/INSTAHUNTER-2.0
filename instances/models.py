from django.db import models
from django.utils import timezone
import os
import uuid


def campaign_upload_path(instance, filename):
    """
    Gera um caminho de upload com nome de arquivo sanitizado
    """
    # Obter extensão do arquivo
    ext = os.path.splitext(filename)[1].lower()
    # Gerar nome único curto
    unique_name = f"{uuid.uuid4().hex[:8]}{ext}"
    # Retornar caminho com data
    return f"campaigns/{timezone.now().strftime('%Y/%m/%d')}/{unique_name}"


class Instance(models.Model):
    """
    Model para armazenar instâncias da Evolution API
    """
    
    INTEGRATION_CHOICES = [
        ('WHATSAPP-BAILEYS', 'WhatsApp Baileys'),
        ('WHATSAPP-BUSINESS', 'WhatsApp Business'),
        ('EVOLUTION', 'Evolution'),
    ]
    
    STATUS_CHOICES = [
        ('created', 'Criada'),
        ('connected', 'Conectada'),
        ('disconnected', 'Desconectada'),
        ('error', 'Erro'),
    ]
    
    # Informações básicas da instância
    instance_name = models.CharField('Nome da Instância', max_length=100, unique=True)
    instance_id = models.CharField('ID da Instância', max_length=200, blank=True, null=True)
    token = models.CharField('Token da Instância', max_length=200, blank=True, null=True)
    number = models.CharField('Número WhatsApp', max_length=20, blank=True, null=True)
    
    # Tipo de integração
    integration_type = models.CharField(
        'Tipo de Integração',
        max_length=50,
        choices=INTEGRATION_CHOICES,
        default='WHATSAPP-BAILEYS'
    )
    
    # Status da conexão
    status = models.CharField(
        'Status',
        max_length=20,
        choices=STATUS_CHOICES,
        default='created'
    )
    
    # QR Code para conexão
    qrcode = models.BooleanField('Gerar QR Code', default=True)
    qrcode_base64 = models.TextField('QR Code Base64', blank=True, null=True)
    
    # Configurações
    reject_call = models.BooleanField('Rejeitar Chamadas', default=False)
    msg_call = models.TextField('Mensagem de Chamada', blank=True, null=True)
    groups_ignore = models.BooleanField('Ignorar Grupos', default=False)
    always_online = models.BooleanField('Sempre Online', default=False)
    read_messages = models.BooleanField('Ler Mensagens', default=False)
    read_status = models.BooleanField('Ler Status', default=False)
    
    # Webhook (opcional)
    webhook_url = models.URLField('URL do Webhook', blank=True, null=True)
    webhook_by_events = models.BooleanField('Webhook por Eventos', default=False)
    webhook_base64 = models.BooleanField('Webhook Base64', default=True)
    
    # Informações de data
    created_at = models.DateTimeField('Criado em', default=timezone.now)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Instância'
        verbose_name_plural = 'Instâncias'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.instance_name} ({self.get_integration_type_display()})'
    
    def is_connected(self):
        return self.status == 'connected'


class Campaign(models.Model):
    """
    Model para armazenar campanhas de envio (agrupamento de mensagens)
    """
    
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Texto'),
        ('image', 'Imagem'),
        ('document', 'Documento'),
        ('audio', 'Áudio'),
        ('video', 'Vídeo'),
        ('sticker', 'Sticker'),
    ]
    
    DISTRIBUTION_MODE_CHOICES = [
        ('imediato', 'Imediato'),
        ('ate_horario', 'Até Horário'),
        ('tempo_total', 'Tempo Total'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('sending', 'Enviando'),
        ('completed', 'Concluída'),
        ('error', 'Erro'),
    ]
    
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE, related_name='campaigns', verbose_name='Instância')
    message_type = models.CharField('Tipo', max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    
    # Conteúdo
    text_content = models.TextField('Mensagem', blank=True, null=True)
    media_file = models.FileField('Arquivo', upload_to=campaign_upload_path, blank=True, null=True)
    media_caption = models.TextField('Legenda', blank=True, null=True)
    media_filename = models.CharField('Nome do Arquivo', max_length=500, blank=True, null=True)
    
    # Estatísticas
    total_recipients = models.IntegerField('Total de Destinatários', default=0)
    success_count = models.IntegerField('Enviados com Sucesso', default=0)
    error_count = models.IntegerField('Erros', default=0)
    
    # Distribuição de tempo
    distribuicao_modo = models.CharField('Modo de Distribuição', max_length=20, choices=DISTRIBUTION_MODE_CHOICES, default='imediato')
    tempo_estimado = models.CharField('Tempo Estimado', max_length=50, blank=True, null=True)
    
    # Status
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    cancelled = models.BooleanField('Cancelado', default=False)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    completed_at = models.DateTimeField('Concluído em', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Campanha'
        verbose_name_plural = 'Campanhas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Campanha {self.id} - {self.instance.instance_name} ({self.success_count}/{self.total_recipients})'


class Message(models.Model):
    """
    Model para armazenar histórico de mensagens enviadas
    """
    
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Texto'),
        ('image', 'Imagem'),
        ('document', 'Documento'),
        ('audio', 'Áudio'),
        ('video', 'Vídeo'),
        ('sticker', 'Sticker'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('sent', 'Enviada'),
        ('error', 'Erro'),
    ]
    
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='messages', verbose_name='Campanha', null=True, blank=True)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE, related_name='messages', verbose_name='Instância')
    recipient = models.CharField('Destinatário', max_length=20, help_text='Número com código do país (ex: 5511999999999)')
    message_type = models.CharField('Tipo', max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    
    # Conteúdo
    text_content = models.TextField('Mensagem', blank=True, null=True)
    media_url = models.URLField('URL da Mídia', blank=True, null=True)
    media_file = models.FileField('Arquivo', upload_to='messages/%Y/%m/%d/', blank=True, null=True)
    media_caption = models.TextField('Legenda', blank=True, null=True)
    media_filename = models.CharField('Nome do Arquivo Original', max_length=255, blank=True, null=True)
    
    # Status e resposta
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    response_data = models.JSONField('Resposta da API', blank=True, null=True)
    error_message = models.TextField('Mensagem de Erro', blank=True, null=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    sent_at = models.DateTimeField('Enviado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Mensagem'
        verbose_name_plural = 'Mensagens'
        ordering = ['-sent_at']
    
    def __str__(self):
        return f'{self.recipient} - {self.get_message_type_display()} ({self.get_status_display()})'
