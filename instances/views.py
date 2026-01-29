from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Instance, Message, Campaign
from .forms import InstanceForm, SendMessageForm, BulkMessageForm
from .services import EvolutionAPIService
from django.utils import timezone


def index(request):
    """
    Página inicial
    """
    instances = Instance.objects.all()[:5]
    context = {
        'instances': instances,
        'total_instances': Instance.objects.count(),
        'connected_instances': Instance.objects.filter(status='connected').count(),
    }
    return render(request, 'instances/index.html', context)


def instance_list(request):
    """
    Lista todas as instâncias
    """
    instances = Instance.objects.all()
    context = {
        'instances': instances
    }
    return render(request, 'instances/instance_list.html', context)


def instance_create(request):
    """
    Cria uma nova instância
    """
    if request.method == 'POST':
        form = InstanceForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            
            # Criar instância na Evolution API
            api_service = EvolutionAPIService()
            instance_data = {
                'instance_name': instance.instance_name,
                'number': instance.number,
                'integration_type': instance.integration_type,
                'qrcode': True,  # Sempre tentar gerar QR Code na criação
                'reject_call': instance.reject_call,
                'msg_call': instance.msg_call,
                'groups_ignore': instance.groups_ignore,
                'always_online': instance.always_online,
                'read_messages': instance.read_messages,
                'read_status': instance.read_status,
                'webhook_url': instance.webhook_url,
                'webhook_by_events': instance.webhook_by_events,
                'webhook_base64': instance.webhook_base64,
            }
            print(f"[instance_create] Chamando api_service.create_instance com dados: {instance_data}")
            result = api_service.create_instance(instance_data)
            print(f"[instance_create] Resultado recebido: {result}")
            
            # Verificar se result é um dicionário
            if not isinstance(result, dict):
                print(f"[instance_create] Erro: result não é dict. Tipo: {type(result)}")
                instance.status = 'error'
                instance.save()
                messages.error(request, f'Erro ao criar instância: Resposta inválida da API')
                return redirect('instances:instance_detail', pk=instance.pk)
            
            if 'error' in result:
                # Mesmo com erro, vamos salvar a instância localmente
                instance.status = 'error'
                instance.save()
                messages.error(request, f'Erro ao criar instância: {result["error"]}')
                return redirect('instances:instance_detail', pk=instance.pk)
            else:
                # Validar que a instância foi criada verificando o status
                status_result = api_service.get_instance_status(instance.instance_name)
                
                if 'error' in status_result:
                    # Instância não existe na API
                    instance.status = 'error'
                    instance.save()
                    messages.error(request, f'Instância criada no banco mas não respondeu na API: {status_result["error"]}')
                    return redirect('instances:instance_detail', pk=instance.pk)
                
                # Armazenar informações retornadas pela API
                instance.instance_id = result.get('instance', {}).get('instanceId') if isinstance(result.get('instance'), dict) else None
                instance.token = result.get('hash') if isinstance(result.get('hash'), str) else None
                print(f"[instance_create] instance_id: {instance.instance_id}, token: {instance.token}")
                
                # Tentar extrair QR Code da resposta de criação
                qrcode_saved = False
                
                print(f"[instance_create] Tentando extrair QR Code. result keys: {result.keys()}")
                
                # Formato 1: result['qrcode']['base64']
                if isinstance(result, dict) and 'qrcode' in result:
                    print(f"[instance_create] 'qrcode' encontrado em result. Tipo: {type(result['qrcode'])}")
                    if isinstance(result['qrcode'], dict) and 'base64' in result['qrcode']:
                        instance.qrcode_base64 = result['qrcode']['base64']
                        qrcode_saved = True
                        instance.status = 'connecting'
                        print(f"[instance_create] ✓ QR Code extraído na criação (formato 1). Tamanho: {len(instance.qrcode_base64)}")
                    # Formato 2: result['qrcode'] já é a string base64
                    elif isinstance(result['qrcode'], str):
                        instance.qrcode_base64 = result['qrcode']
                        qrcode_saved = True
                        instance.status = 'connecting'
                        print(f"[instance_create] ✓ QR Code extraído na criação (formato 2). Tamanho: {len(instance.qrcode_base64)}")
                else:
                    print(f"[instance_create] 'qrcode' NÃO encontrado em result")
                
                # Se não conseguir extrair, deixar em status created
                if not qrcode_saved:
                    instance.status = 'created'
                    print(f"[instance_create] ⚠ Não foi possível extrair QR Code na criação")
                
                print(f"[instance_create] Salvando instância. qrcode_saved: {qrcode_saved}, status: {instance.status}")
                instance.save()
                print(f"[instance_create] Instância salva. ID: {instance.pk}")
                
                if qrcode_saved:
                    messages.success(request, 'Instância criada com sucesso! QR Code gerado. Escaneie com seu WhatsApp.')
                else:
                    messages.success(request, 'Instância criada com sucesso! Clique em "Conectar / Gerar QR Code" para conectar.')
                
                return redirect('instances:instance_detail', pk=instance.pk)
    else:
        form = InstanceForm()
    
    context = {
        'form': form,
        'title': 'Nova Instância'
    }
    return render(request, 'instances/instance_form.html', context)


def instance_detail(request, pk):
    """
    Detalhes de uma instância
    """
    instance = get_object_or_404(Instance, pk=pk)
    context = {
        'instance': instance
    }
    return render(request, 'instances/instance_detail.html', context)


def instance_edit(request, pk):
    """
    Edita uma instância
    """
    instance = get_object_or_404(Instance, pk=pk)
    
    if request.method == 'POST':
        form = InstanceForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Instância atualizada com sucesso!')
            return redirect('instances:instance_detail', pk=instance.pk)
    else:
        form = InstanceForm(instance=instance)
    
    context = {
        'form': form,
        'instance': instance,
        'title': 'Editar Instância'
    }
    return render(request, 'instances/instance_form.html', context)


def instance_delete(request, pk):
    """
    Deleta uma instância
    """
    instance = get_object_or_404(Instance, pk=pk)
    
    if request.method == 'POST':
        # Deletar apenas localmente (sem chamar Evolution API)
        instance.delete()
        messages.success(request, 'Instância deletada com sucesso!')
        return redirect('instances:instance_list')
    
    context = {
        'instance': instance
    }
    return render(request, 'instances/instance_confirm_delete.html', context)


def instance_connect(request, pk):
    """
    Conecta uma instância (verifica status de conexão)
    """
    instance = get_object_or_404(Instance, pk=pk)
    
    print(f"[DEBUG] Iniciando conexão da instância: {instance.instance_name} (Status: {instance.status})")
    
    # Verificar se a instância foi criada com sucesso
    if instance.status == 'error':
        messages.error(request, 'Instância não foi criada na Evolution API. Verifique os logs e tente criar novamente.')
        return redirect('instances:instance_detail', pk=instance.pk)
    
    # Verificar conexão com Evolution API
    api_service = EvolutionAPIService()
    connection_check = api_service.check_connection()
    if connection_check['status'] == 'error':
        messages.error(request, f'❌ Erro de conexão com Evolution API: {connection_check["message"]}. Verifique se o serviço está rodando e a URL está correta.')
        return redirect('instances:instance_detail', pk=instance.pk)
    
    # Conectar/verificar status
    result = api_service.connect_instance(instance.instance_name, instance.number)
    
    print(f"[DEBUG] Connect Result: {result}")
    
    if 'error' in result:
        messages.error(request, f'Erro ao conectar instância: {result["error"]}')
    else:
        # Resposta esperada: {"instance": {"instanceName": "...", "state": "open/connecting/..."}}
        instance_data = result.get('instance', {})
        state = instance_data.get('state', 'unknown')
        
        print(f"[DEBUG] Estado da instância: {state}")
        
        if state == 'open':
            instance.status = 'connected'
            instance.save()
            messages.success(request, '✓ Instância conectada com sucesso! Aguarde a sincronização.')
        elif state == 'connecting':
            if instance.status != 'connecting':
                instance.status = 'connecting'
                instance.save()
            messages.info(request, '⏳ Instância em processo de conexão. Aguarde alguns segundos e verifique novamente.')
        else:
            instance.status = state
            instance.save()
            messages.info(request, f'Estado da instância: {state}')
    
    return redirect('instances:instance_detail', pk=pk)


def instance_disconnect(request, pk):
    """
    Desconecta uma instância
    """
    instance = get_object_or_404(Instance, pk=pk)
    
    api_service = EvolutionAPIService()
    result = api_service.logout_instance(instance.instance_name)
    
    if 'error' in result:
        messages.error(request, f'Erro ao desconectar instância: {result["error"]}')
    else:
        instance.status = 'disconnected'
        instance.qrcode_base64 = None
        instance.save()
        messages.success(request, 'Instância desconectada com sucesso!')
    
    return redirect('instances:instance_detail', pk=pk)


def instance_restart(request, pk):
    """
    Reinicia uma instância
    """
    instance = get_object_or_404(Instance, pk=pk)
    
    api_service = EvolutionAPIService()
    result = api_service.restart_instance(instance.instance_name)
    
    if 'error' in result:
        messages.error(request, f'Erro ao reiniciar instância: {result["error"]}')
    else:
        messages.success(request, 'Instância reiniciada com sucesso!')
    
    return redirect('instances:instance_detail', pk=pk)


def instance_status(request, pk):
    """
    Obtém o status de uma instância (Ajax)
    """
    instance = get_object_or_404(Instance, pk=pk)
    
    api_service = EvolutionAPIService()
    result = api_service.get_instance_status(instance.instance_name)
    
    if 'error' not in result:
        # Atualizar status no banco
        state = result.get('instance', {}).get('state')
        if state == 'open':
            instance.status = 'connected'
        elif state == 'close':
            instance.status = 'disconnected'
        instance.save()
    
    return JsonResponse(result)


# ===== VIEWS DE MENSAGENS =====

def message_send(request):
    """
    Formulário para enviar mensagem (individual ou em massa)
    """
    if request.method == 'POST':
        form = SendMessageForm(request.POST, request.FILES)
        
        if not form.is_valid():
            print(f"Erros no formulário: {form.errors}")
        
        if form.is_valid():
            instance = form.cleaned_data['instance']
            recipients = form.cleaned_data['recipients']
            message_type = form.cleaned_data['message_type']
            text_content = form.cleaned_data.get('text_content')
            media_file = form.cleaned_data.get('media_file')
            media_caption = form.cleaned_data.get('media_caption')
            
            # Preparar contatos para webhook do n8n
            contatos = []
            for recipient in recipients:
                contatos.append({
                    "Telefone": recipient,
                    "Mensagem": text_content if message_type == 'text' else media_caption or ""
                })
            
            # Preparar dados do arquivo se existir
            arquivo_data = None
            if media_file:
                # Salvar arquivo em Message temporário para pegar o path
                temp_message = Message.objects.create(
                    instance=instance,
                    recipient='temp',
                    message_type=message_type,
                    media_file=media_file,
                    media_caption=media_caption,
                    media_filename=media_file.name,
                    status='pending'
                )
                
                api_service = EvolutionAPIService()
                media_base64 = api_service.file_to_base64(temp_message.media_file.path)
                
                arquivo_data = {
                    "nome": media_file.name,
                    "tipo": media_file.content_type,
                    "tamanho": media_file.size,
                    "base64": media_base64
                }
                
                temp_message.delete()  # Limpar arquivo temporário
            
            # Enviar para webhook do n8n
            api_service = EvolutionAPIService()
            webhook_result = api_service.send_to_n8n_webhook(
                instance_id=str(instance.id),
                instance_name=instance.instance_name,
                contatos=contatos,
                arquivo_data=arquivo_data
            )
            
            if 'error' in webhook_result:
                messages.error(request, f'Erro ao enviar para webhook: {webhook_result["error"]}')
                return render(request, 'instances/message_send.html', {'form': form})
            
            messages.success(request, f'{len(recipients)} contatos enviados para o webhook com sucesso!')
            return redirect('instances:message_history')
    else:
        form = SendMessageForm()
    
    context = {
        'form': form,
        'title': 'Enviar Mensagem'
    }
    return render(request, 'instances/message_send.html', context)


def message_bulk(request):
    """
    Formulário para envio em massa
    """
    if request.method == 'POST':
        form = BulkMessageForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.cleaned_data['instance']
            recipients = form.cleaned_data['recipients']
            message_type = form.cleaned_data['message_type']
            text_content = form.cleaned_data.get('text_content')
            media_file = form.cleaned_data.get('media_file')
            media_caption = form.cleaned_data.get('media_caption')
            
            # Preparar contatos para webhook do n8n
            contatos = []
            for recipient in recipients:
                contatos.append({
                    "Telefone": recipient,
                    "Mensagem": text_content if message_type == 'text' else media_caption or ""
                })
            
            # Preparar dados do arquivo se existir
            arquivo_data = None
            if media_file:
                # Salvar arquivo em Message temporário para pegar o path
                temp_message = Message.objects.create(
                    instance=instance,
                    recipient='temp',
                    message_type=message_type,
                    media_file=media_file,
                    media_caption=media_caption,
                    media_filename=media_file.name,
                    status='pending'
                )
                
                api_service = EvolutionAPIService()
                media_base64 = api_service.file_to_base64(temp_message.media_file.path)
                
                arquivo_data = {
                    "nome": media_file.name,
                    "tipo": media_file.content_type,
                    "tamanho": media_file.size,
                    "base64": media_base64
                }
                
                temp_message.delete()  # Limpar arquivo temporário
            
            # Enviar para webhook do n8n
            api_service = EvolutionAPIService()
            webhook_result = api_service.send_to_n8n_webhook(
                instance_id=str(instance.id),
                instance_name=instance.instance_name,
                contatos=contatos,
                arquivo_data=arquivo_data
            )
            
            if 'error' in webhook_result:
                messages.error(request, f'Erro ao enviar para webhook: {webhook_result["error"]}')
                return render(request, 'instances/message_bulk.html', {'form': form})
            
            messages.success(request, f'{len(recipients)} contatos enviados para o webhook com sucesso!')
            return redirect('instances:message_history')
    else:
        form = BulkMessageForm()
    
    context = {
        'form': form,
        'title': 'Envio em Massa'
    }
    return render(request, 'instances/message_bulk.html', context)


def message_history(request):
    """
    Lista o histórico de mensagens enviadas
    """
    messages_list = Message.objects.all().select_related('instance').order_by('-created_at')
    
    # Filtros opcionais
    instance_id = request.GET.get('instance')
    status = request.GET.get('status')
    
    if instance_id:
        messages_list = messages_list.filter(instance_id=instance_id)
    if status:
        messages_list = messages_list.filter(status=status)
    
    # Limitar a 500 mensagens mais recentes para melhor performance
    messages_list = messages_list[:500]
    
    context = {
        'messages': messages_list,
        'instances': Instance.objects.all(),
        'selected_instance': instance_id,
        'selected_status': status,
    }
    return render(request, 'instances/message_history.html', context)


def message_clear_errors(request):
    """
    Limpa mensagens com erro ou pendentes antigas
    """
    if request.method == 'POST':
        # Deletar mensagens com erro
        deleted = Message.objects.filter(status='error').delete()
        messages.success(request, f'{deleted[0]} mensagens com erro foram removidas.')
    
    return redirect('instances:message_history')


def campaign_history(request):
    """
    Lista o histórico de campanhas
    """
    campaigns_list = Campaign.objects.all().select_related('instance').order_by('-created_at')
    
    # Filtros opcionais
    instance_id = request.GET.get('instance')
    status = request.GET.get('status')
    
    if instance_id:
        campaigns_list = campaigns_list.filter(instance_id=instance_id)
    if status:
        campaigns_list = campaigns_list.filter(status=status)
    
    # Limitar a 100 campanhas mais recentes
    campaigns_list = campaigns_list[:100]
    
    context = {
        'campaigns': campaigns_list,
        'instances': Instance.objects.all(),
        'selected_instance': instance_id,
        'selected_status': status,
    }
    return render(request, 'instances/campaign_history.html', context)


def campaign_detail(request, pk):
    """
    Detalhes de uma campanha com todas as mensagens
    """
    campaign = get_object_or_404(Campaign, pk=pk)
    messages_list = campaign.messages.all().order_by('-created_at')
    
    context = {
        'campaign': campaign,
        'messages': messages_list,
    }
    return render(request, 'instances/campaign_detail.html', context)


def campaign_cancel(request, pk):
    """
    Cancela uma campanha em andamento
    """
    campaign = get_object_or_404(Campaign, pk=pk)
    
    if campaign.status == 'sending':
        campaign.cancelled = True
        campaign.status = 'error'
        campaign.save()
    
    return redirect('instances:campaign_detail', pk=pk)

