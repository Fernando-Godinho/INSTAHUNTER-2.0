from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Instance, Contact, Message
from .services import EvolutionAPIService
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def webhook_waba(request):
    """
    Webhook para receber eventos do WhatsApp WABA (via N8N ou direto)
    """
    print(f"[DEBUG] Webhook recebido: {request.method}")
    if request.method == 'GET':
        # Verificação do webhook (hub.verify_token)
        verify_token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        if verify_token:
            print(f"[DEBUG] Verificação de Webhook - Token: {verify_token}")
            return HttpResponse(challenge)
        return HttpResponse("Webhook Active")

    if request.method == 'POST':
        try:
            raw_data = request.body.decode('utf-8')
            print(f"[DEBUG] Webhook Body: {raw_data[:1000]}") # Log mais longo
            data = json.loads(raw_data)
            
            # O JSON recebido pode ser uma lista (n8n às vezes envia assim)
            if isinstance(data, list):
                data = data[0]
            
            # Extrair corpo real se estiver encapsulado
            body_data = data.get('body', data)
            
            # 1. Verificar se é um log manual de OUT (vire n8n)
            # Aceitamos 'direction' no topo ou dentro de 'body'
            direction = data.get('direction') or body_data.get('direction')
            if direction == 'OUT':
                wa_id_raw = (data.get('contact_number') or body_data.get('contact_number') or "")
                # Limpar wa_id: manter apenas números
                wa_id = "".join(filter(str.isdigit, wa_id_raw))
                text_content = data.get('text') or body_data.get('text') or ""
                
                if wa_id:
                    instance = Instance.objects.filter(status='connected').first() or Instance.objects.first()
                    if not instance:
                        # Criar instância padrão se não existir para não perder o log
                        instance = Instance.objects.create(
                            instance_name="Produção",
                            instance_id="prod",
                            status='connected'
                        )
                        print(f"[DEBUG] Instância auto-criada: {instance.instance_name}")

                    contact, _ = Contact.objects.get_or_create(
                        instance=instance,
                        number=wa_id,
                        defaults={'name': wa_id}
                    )
                    Message.objects.create(
                        instance=instance,
                        contact=contact,
                        recipient=wa_id,
                        direction='OUT',
                        message_type='text',
                        text_content=text_content,
                        status='sent'
                    )
                    contact.last_message_at = timezone.now()
                    contact.save()
                    print(f"[DEBUG] Log OUT manual salvo para {wa_id}")
                    return JsonResponse({"status": "success"})

            # 2. Estrutura WABA Padrão
            entries = body_data.get('entry', [])
            
            if not entries:
                print(f"[DEBUG] Aviso: Nenhum 'entry' encontrado. Keys: {list(body_data.keys())}")
            
            for entry in entries:
                changes = entry.get('changes', [])
                for change in changes:
                    value = change.get('value', {})
                    messages = value.get('messages', {})
                    contacts_payload = value.get('contacts', [])
                    
                    if not messages:
                        continue
                        
                    print(f"[DEBUG] Processando {len(messages)} mensagens")
                    
                    # Mapear contatos para facilitar
                    contact_info = {}
                    for c in contacts_payload:
                        contact_info[c.get('wa_id')] = c.get('profile', {}).get('name')

                    # Processar mensagens
                    for msg in messages:
                        wa_id_raw = msg.get('from')
                        # Limpar wa_id: manter apenas números
                        wa_id = "".join(filter(str.isdigit, wa_id_raw))
                        wamid = msg.get('id')
                        timestamp = msg.get('timestamp')
                        msg_type = msg.get('type')
                        
                        instance = Instance.objects.filter(status='connected').first() or Instance.objects.first()
                        if not instance:
                            instance = Instance.objects.create(
                                instance_name="Produção",
                                instance_id="prod",
                                status='connected'
                            )
                            print(f"[DEBUG] Instância auto-criada para INbound")

                        # Criar ou atualizar contato
                        contact_name = contact_info.get(msg.get('from'))
                        contact, created = Contact.objects.get_or_create(
                            instance=instance,
                            number=wa_id,
                            defaults={'name': contact_name or wa_id}
                        )
                        if contact_name and contact.name != contact_name:
                            contact.name = contact_name
                            contact.save()
                        
                        print(f"[DEBUG] Contato: {contact.name} ({contact.number})")

                        # Salvar mensagem se não existir
                        if not Message.objects.filter(wamid=wamid).exists():
                            text_content = ""
                            if msg_type == 'text':
                                text_content = msg.get('text', {}).get('body', '')
                            elif msg_type == 'button':
                                text_content = msg.get('button', {}).get('text', '')
                            elif msg_type == 'interactive':
                                text_content = "[Mensagem Interativa]"
                            else:
                                text_content = f"[{msg_type.capitalize()}]"

                            Message.objects.create(
                                instance=instance,
                                contact=contact,
                                recipient=wa_id,
                                direction='IN',
                                wamid=wamid,
                                message_type=msg_type if msg_type in dict(Message.MESSAGE_TYPE_CHOICES) else 'text',
                                text_content=text_content,
                                status='sent',
                                created_at=timezone.datetime.fromtimestamp(int(timestamp)) if timestamp else timezone.now()
                            )
                            print(f"[DEBUG] Mensagem salva: {text_content[:50]}")
                            
                            # Atualizar timestamp do contato
                            contact.last_message_at = timezone.now()
                            contact.save()
                        else:
                            print(f"[DEBUG] Mensagem duplicada ignorada: {wamid}")

            return JsonResponse({"status": "success"})
        except Exception as e:
            print(f"[DEBUG] ERRO CRÍTICO NO WEBHOOK: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return HttpResponse(status=405)

def chat_view(request):
    """
    Tela principal do Chat
    """
    contacts = Contact.objects.all().order_by('-last_message_at')
    return render(request, 'instances/chat.html', {
        'contacts': contacts
    })

def chat_contacts(request):
    """
    Retorna apenas a lista de contatos (fragmento HTMX)
    """
    contacts = Contact.objects.all().order_by('-last_message_at')
    return render(request, 'instances/chat_contacts_partial.html', {
        'contacts': contacts
    })

def chat_messages(request, contact_id):
    """
    Carrega o esqueleto do chat (header + container de mensagens + input)
    """
    contact = get_object_or_404(Contact, id=contact_id)
    # Pegamos as mensagens para a carga inicial
    messages_list = Message.objects.filter(contact=contact).order_by('created_at')
    return render(request, 'instances/chat_messages_partial.html', {
        'contact': contact,
        'messages_list': messages_list
    })

def chat_messages_only(request, contact_id):
    """
    Carrega APENAS a lista de mensagens (para polling HTMX)
    """
    contact = get_object_or_404(Contact, id=contact_id)
    messages_list = Message.objects.filter(contact=contact).order_by('created_at')
    return render(request, 'instances/chat_messages_only_partial.html', {
        'contact': contact,
        'messages_list': messages_list
    })

def chat_send_message(request, contact_id):
    """
    Envia uma mensagem de texto pelo chat
    """
    if request.method == 'POST':
        contact = get_object_or_404(Contact, id=contact_id)
        text = request.POST.get('message')
        
        if not text:
            return HttpResponse(status=400)
            
        service = EvolutionAPIService()
        # Enviar via Evolution API (ou N8N como configurado no services.py)
        # Se send_to_n8n_webhook estiver ativo, usamos ele
        
        # Preparar contatos no formato do n8n (o projeto parece estar usando n8n agora)
        contatos = [{"Telefone": contact.number, "Mensagem": text}]
        
        # Tentar enviar
        res = service.send_to_n8n_webhook(
            instance_id=contact.instance.instance_id or "1",
            instance_name=contact.instance.instance_name,
            contatos=contatos
        )
        
        if 'error' not in res:
            # Salvar no banco local como OUT
            Message.objects.create(
                instance=contact.instance,
                contact=contact,
                recipient=contact.number,
                direction='OUT',
                message_type='text',
                text_content=text,
                status='sent'
            )
            # Atualizar contato
            contact.last_message_at = timezone.now()
            contact.save()
            
            # Retornar o fragmento de mensagens atualizado
            messages_list = Message.objects.filter(contact=contact).order_by('created_at')
            return render(request, 'instances/chat_messages_partial.html', {
                'contact': contact,
                'messages_list': messages_list
            })
        else:
            return JsonResponse(res, status=500)
            
    return HttpResponse(status=405)

@csrf_exempt
def chat_delete_contact(request, contact_id):
    """
    Exclui um contato e todas as suas mensagens
    """
    if request.method == 'DELETE':
        contact = get_object_or_404(Contact, id=contact_id)
        contact_name = contact.name
        contact.delete()
        print(f"[DEBUG] Contato deletado: {contact_name}")
        # Retorna a lista de contatos atualizada
        contacts = Contact.objects.all().order_by('-last_message_at')
        return render(request, 'instances/chat_contacts_partial.html', {
            'contacts': contacts
        })
    return HttpResponse(status=405)
