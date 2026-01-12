from django import forms
from .models import Instance, Message


class InstanceForm(forms.ModelForm):
    """
    Formulário para criar/editar instâncias
    """
    
    class Meta:
        model = Instance
        fields = [
            'instance_name',
            'number',
            'integration_type',
            'qrcode',
            'reject_call',
            'msg_call',
            'groups_ignore',
            'always_online',
            'read_messages',
            'read_status',
            'webhook_url',
            'webhook_by_events',
            'webhook_base64',
        ]
        
        widgets = {
            'instance_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome da instância'
            }),
            'number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '5511999999999 (com código do país)'
            }),
            'integration_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'msg_call': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Mensagem automática para chamadas'
            }),
            'webhook_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://seu-webhook.com/endpoint'
            }),
            'qrcode': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'reject_call': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'groups_ignore': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'always_online': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'read_messages': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'read_status': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'webhook_by_events': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'webhook_base64': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class SendMessageForm(forms.Form):
    """
    Formulário para enviar mensagens
    """
    instance = forms.ModelChoiceField(
        queryset=Instance.objects.filter(status='connected'),
        label='Instância',
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Selecione a instância conectada'
    )
    
    recipients = forms.CharField(
        label='Número(s) do(s) Destinatário(s)',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': '5511999999999\n5511988888888\n5511977777777'
        }),
        help_text='Um número por linha (com código do país). Para envio único, adicione apenas um número.'
    )
    
    message_type = forms.ChoiceField(
        label='Tipo de Mensagem',
        choices=[
            ('text', 'Texto'),
            ('image', 'Imagem'),
            ('document', 'Documento'),
            ('audio', 'Áudio'),
            ('video', 'Vídeo'),
            ('sticker', 'Sticker'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='image'  # Alterado para 'image' para mostrar campos de upload por padrão
    )
    
    text_content = forms.CharField(
        label='Mensagem',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Digite sua mensagem aqui...'
        })
    )
    
    media_file = forms.FileField(
        label='Arquivo',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,video/*,audio/*,.pdf,.doc,.docx,.xls,.xlsx,.txt,.zip'
        }),
        help_text='Envie uma foto, vídeo, áudio ou documento'
    )
    
    media_caption = forms.CharField(
        label='Legenda (opcional)',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Legenda da mídia...'
        })
    )
    
    # Campos de distribuição de tempo
    distribuicao_modo = forms.ChoiceField(
        label='Modo de Envio',
        choices=[
            ('imediato', 'Imediato (1-3s entre mensagens)'),
            ('ate_horario', 'Distribuir até um horário'),
            ('tempo_total', 'Distribuir em um período'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='imediato',
        help_text='Como distribuir o envio das mensagens'
    )
    
    hora_limite = forms.IntegerField(
        label='Hora Limite',
        required=False,
        min_value=0,
        max_value=23,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '17'
        }),
        help_text='Hora até quando enviar (formato 24h). Ex: 17 para 17h'
    )
    
    tempo_total_minutos = forms.IntegerField(
        label='Tempo Total (minutos)',
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '60'
        }),
        help_text='Tempo total em minutos para distribuir os envios'
    )
    
    def clean_recipients(self):
        """Processa e valida os destinatários"""
        recipients = self.cleaned_data.get('recipients', '')
        recipients_list = [r.strip() for r in recipients.split('\n') if r.strip()]
        
        if not recipients_list:
            raise forms.ValidationError('Pelo menos um destinatário é necessário.')
        
        return recipients_list
    
    def clean(self):
        cleaned_data = super().clean()
        message_type = cleaned_data.get('message_type')
        text_content = cleaned_data.get('text_content')
        media_file = cleaned_data.get('media_file')
        
        if message_type == 'text' and not text_content:
            raise forms.ValidationError('Para mensagem de texto, o campo Mensagem é obrigatório.')
        
        if message_type != 'text' and not media_file:
            raise forms.ValidationError('Para mensagens de mídia, é necessário enviar um arquivo.')
        
        # Validação de tipo de arquivo
        if media_file:
            file_name = media_file.name.lower()
            file_size = media_file.size
            
            # Limite de 16MB
            if file_size > 16 * 1024 * 1024:
                raise forms.ValidationError('O arquivo não pode exceder 16MB.')
            
            # Validações por tipo
            if message_type == 'image':
                if not any(file_name.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    raise forms.ValidationError('Para imagens, use arquivos JPG, PNG, GIF ou WEBP.')
            elif message_type == 'video':
                if not any(file_name.endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']):
                    raise forms.ValidationError('Para vídeos, use arquivos MP4, AVI, MOV, MKV ou WEBM.')
            elif message_type == 'audio':
                if not any(file_name.endswith(ext) for ext in ['.mp3', '.ogg', '.wav', '.m4a', '.aac']):
                    raise forms.ValidationError('Para áudios, use arquivos MP3, OGG, WAV, M4A ou AAC.')
            elif message_type == 'sticker':
                if not any(file_name.endswith(ext) for ext in ['.png', '.webp']):
                    raise forms.ValidationError('Para stickers, use arquivos PNG ou WEBP.')
        
        return cleaned_data


class BulkMessageForm(forms.Form):
    """
    Formulário para envio em massa
    """
    instance = forms.ModelChoiceField(
        queryset=Instance.objects.filter(status='connected'),
        label='Instância',
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Selecione a instância conectada'
    )
    
    recipients = forms.CharField(
        label='Números dos Destinatários',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': '5511999999999\n5511988888888\n5511977777777'
        }),
        help_text='Um número por linha, com código do país'
    )
    
    message_type = forms.ChoiceField(
        label='Tipo de Mensagem',
        choices=[
            ('text', 'Texto'),
            ('image', 'Imagem'),
            ('document', 'Documento'),
            ('audio', 'Áudio'),
            ('video', 'Vídeo'),
            ('sticker', 'Sticker'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='text'
    )
    
    text_content = forms.CharField(
        label='Mensagem',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Digite sua mensagem aqui...'
        })
    )
    
    media_file = forms.FileField(
        label='Arquivo',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,video/*,audio/*,.pdf,.doc,.docx,.xls,.xlsx,.txt,.zip'
        }),
        help_text='Envie uma foto, vídeo, áudio ou documento para enviar a todos'
    )
    
    media_caption = forms.CharField(
        label='Legenda (opcional)',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Legenda da mídia...'
        })
    )
    
    # Campos de distribuição de tempo
    distribuicao_modo = forms.ChoiceField(
        label='Modo de Envio',
        choices=[
            ('imediato', 'Imediato (1-3s entre mensagens)'),
            ('ate_horario', 'Distribuir até um horário'),
            ('tempo_total', 'Distribuir em um período'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='imediato',
        help_text='Como distribuir o envio das mensagens'
    )
    
    hora_limite = forms.IntegerField(
        label='Hora Limite',
        required=False,
        min_value=0,
        max_value=23,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '17'
        }),
        help_text='Hora até quando enviar (formato 24h). Ex: 17 para 17h'
    )
    
    tempo_total_minutos = forms.IntegerField(
        label='Tempo Total (minutos)',
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '60'
        }),
        help_text='Tempo total em minutos para distribuir os envios'
    )
    
    def clean_recipients(self):
        recipients = self.cleaned_data['recipients']
        numbers = [num.strip() for num in recipients.split('\n') if num.strip()]
        
        if not numbers:
            raise forms.ValidationError('Adicione pelo menos um número.')
        
        # Validar formato básico
        for num in numbers:
            if not num.isdigit() or len(num) < 10:
                raise forms.ValidationError(f'Número inválido: {num}')
        
        return numbers
    
    def clean(self):
        cleaned_data = super().clean()
        message_type = cleaned_data.get('message_type')
        text_content = cleaned_data.get('text_content')
        media_file = cleaned_data.get('media_file')
        
        if message_type == 'text' and not text_content:
            raise forms.ValidationError('Para mensagem de texto, o campo Mensagem é obrigatório.')
        
        if message_type != 'text' and not media_file:
            raise forms.ValidationError('Para mensagens de mídia, é necessário enviar um arquivo.')
        
        # Validação de tipo de arquivo
        if media_file:
            file_name = media_file.name.lower()
            file_size = media_file.size
            
            if file_size > 16 * 1024 * 1024:
                raise forms.ValidationError('O arquivo não pode exceder 16MB.')
            
            if message_type == 'image':
                if not any(file_name.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    raise forms.ValidationError('Para imagens, use arquivos JPG, PNG, GIF ou WEBP.')
            elif message_type == 'video':
                if not any(file_name.endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']):
                    raise forms.ValidationError('Para vídeos, use arquivos MP4, AVI, MOV, MKV ou WEBM.')
            elif message_type == 'audio':
                if not any(file_name.endswith(ext) for ext in ['.mp3', '.ogg', '.wav', '.m4a', '.aac']):
                    raise forms.ValidationError('Para áudios, use arquivos MP3, OGG, WAV, M4A ou AAC.')
            elif message_type == 'sticker':
                if not any(file_name.endswith(ext) for ext in ['.png', '.webp']):
                    raise forms.ValidationError('Para stickers, use arquivos PNG ou WEBP.')
        
        return cleaned_data
