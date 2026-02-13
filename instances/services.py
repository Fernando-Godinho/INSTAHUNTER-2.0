import requests
import base64
import mimetypes
from django.conf import settings
from typing import Dict, Optional
from pathlib import Path


class EvolutionAPIService:
    """
    Serviço para integração com a Evolution API
    """
    
    def __init__(self):
        self.base_url = settings.EVOLUTION_API_URL
        self.api_key = settings.EVOLUTION_API_KEY
        self.headers = {
            'apikey': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def check_connection(self) -> Dict:
        """
        Verifica a conectividade com a Evolution API
        """
        print(f"[DEBUG] Verificando conexão com Evolution API")
        print(f"[DEBUG] URL: {self.base_url}")
        print(f"[DEBUG] API Key: {self.api_key[:20]}...")
        
        try:
            # Tentar acessar o endpoint de fetch instances
            response = requests.get(
                f"{self.base_url}/instance/fetchInstances", 
                headers=self.headers, 
                timeout=10
            )
            print(f"[DEBUG] Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"[DEBUG] ✓ Conexão OK com a Evolution API")
                return {'status': 'success', 'message': 'Conectado à Evolution API'}
            else:
                print(f"[DEBUG] ✗ Status inesperado: {response.status_code}")
                return {'status': 'error', 'message': f'Status {response.status_code}', 'details': response.text}
                
        except requests.exceptions.Timeout:
            print(f"[DEBUG] ✗ Timeout - Evolution API não responde")
            return {'status': 'error', 'message': 'Timeout - Evolution API não responde'}
        except requests.exceptions.ConnectionError:
            print(f"[DEBUG] ✗ Erro de conexão")
            return {'status': 'error', 'message': 'Erro de conexão - verifique a URL e firewall'}
        except Exception as e:
            print(f"[DEBUG] ✗ Erro: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def create_instance(self, instance_data: Dict) -> Dict:
        """
        Cria uma nova instância na Evolution API
        """
        url = f"{self.base_url}/instance/create"
        
        payload = {
            "instanceName": instance_data['instance_name'],
            "qrcode": instance_data.get('qrcode', True),
            "integration": instance_data.get('integration_type', 'WHATSAPP-BAILEYS'),
            "token": instance_data.get('token', self.api_key),  # Token é obrigatório
        }
        
        # Adicionar número se fornecido
        if instance_data.get('number'):
            payload['number'] = instance_data['number']
        
        # Configurações
        if instance_data.get('reject_call'):
            payload['rejectCall'] = instance_data['reject_call']
            if instance_data.get('msg_call'):
                payload['msgCall'] = instance_data['msg_call']
        
        if instance_data.get('groups_ignore'):
            payload['groupsIgnore'] = instance_data['groups_ignore']
        
        if instance_data.get('always_online'):
            payload['alwaysOnline'] = instance_data['always_online']
        
        if instance_data.get('read_messages'):
            payload['readMessages'] = instance_data['read_messages']
        
        if instance_data.get('read_status'):
            payload['readStatus'] = instance_data['read_status']
        
        # Webhook
        if instance_data.get('webhook_url'):
            payload['webhook'] = {
                'url': instance_data['webhook_url'],
                'byEvents': instance_data.get('webhook_by_events', False),
                'base64': instance_data.get('webhook_base64', True),
            }
        
        print(f"[DEBUG] Criando instância - URL: {url}")
        print(f"[DEBUG] Payload: {payload}")
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            print(f"[DEBUG] Status Code: {response.status_code}")
            print(f"[DEBUG] Response: {response.text}")
            response.raise_for_status()
            
            # Tentar fazer parse do JSON
            try:
                result = response.json()
                print(f"[DEBUG] Resposta JSON: {result}")
                
                # Extrair QR Code da resposta se disponível
                if 'qrcode' in result and isinstance(result['qrcode'], dict) and 'base64' in result['qrcode']:
                    print(f"[DEBUG] ✓ QR Code obtido na criação!")
                elif 'qrcode' in result and isinstance(result['qrcode'], str):
                    print(f"[DEBUG] ✓ QR Code (string) obtido na criação!")
                
                return result
            except ValueError:
                return {'error': f'Resposta inválida da API: {response.text}'}
                
        except requests.exceptions.RequestException as e:
            print(f"[DEBUG] Erro: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"[DEBUG] Erro Response: {e.response.text}")
                return {'error': f'{str(e)} - {e.response.text}'}
            return {'error': str(e)}
    
    def get_instance_status(self, instance_name: str) -> Dict:
        """
        Obtém o status de conexão de uma instância
        """
        url = f"{self.base_url}/instance/connectionState/{instance_name}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def connect_instance(self, instance_name: str, number: Optional[str] = None) -> Dict:
        """
        Conecta uma instância (obtém informações de conexão)
        Usa o endpoint GET /instance/connect/{instanceName}
        
        Retorna:
        {
            "instance": {
                "instanceName": "RHINO",
                "state": "open"  # ou "connecting", "disconnected"
            }
        }
        """
        print(f"[DEBUG] Conectando instância: {instance_name}")
        
        # Endpoint principal: GET /instance/connect/{instanceName}
        connect_url = f"{self.base_url}/instance/connect/{instance_name}"
        
        print(f"[DEBUG] URL de conexão: {connect_url}")
        print(f"[DEBUG] Enviando GET para {connect_url}")
        
        try:
            response = requests.get(connect_url, headers=self.headers, timeout=30)
            
            print(f"[DEBUG] Status Code: {response.status_code}")
            print(f"[DEBUG] Response: {response.text[:1000]}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"[DEBUG] ✓ Conexão bem-sucedida!")
                    print(f"[DEBUG] Response JSON: {result}")
                    
                    # Estrutura esperada:
                    # {"instance": {"instanceName": "...", "state": "open/connecting/..."}}
                    
                    return result
                except Exception as parse_error:
                    print(f"[DEBUG] Erro ao fazer parse do JSON: {str(parse_error)}")
                    return {'error': f'Resposta inválida da API: {response.text}'}
            
            elif response.status_code == 404:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('response', {}).get('message', [error_data.get('error', 'Não encontrado')])
                    if isinstance(error_msg, list):
                        error_msg = ' - '.join(error_msg)
                except:
                    error_msg = 'Instância não encontrada'
                
                return {'error': f'Instância não existe na API: {error_msg}'}
            
            else:
                print(f"[DEBUG] ✗ Status inesperado: {response.status_code}")
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Erro desconhecido')
                except:
                    error_msg = response.text[:200]
                
                return {'error': f'Erro ao conectar instância (Status {response.status_code}): {error_msg}'}
                    
        except requests.exceptions.Timeout:
            print(f"[DEBUG] ✗ Timeout na requisição")
            return {'error': 'Timeout ao conectar instância (requisição demorou muito)'}
        except requests.exceptions.RequestException as e:
            print(f"[DEBUG] ✗ Erro na requisição: {str(e)}")
            return {'error': f'Erro de conexão: {str(e)}'}
        except Exception as e:
            print(f"[DEBUG] ✗ Erro inesperado: {str(e)}")
            return {'error': f'Erro inesperado: {str(e)}'}
    
    def restart_instance(self, instance_name: str) -> Dict:
        """
        Reinicia uma instância
        """
        url = f"{self.base_url}/instance/restart/{instance_name}"
        
        try:
            response = requests.post(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def logout_instance(self, instance_name: str) -> Dict:
        """
        Desconecta uma instância (logout)
        """
        url = f"{self.base_url}/instance/logout/{instance_name}"
        
        try:
            response = requests.delete(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def delete_instance(self, instance_name: str) -> Dict:
        """
        Deleta uma instância
        """
        url = f"{self.base_url}/instance/delete/{instance_name}"
        
        try:
            response = requests.delete(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def fetch_instances(self) -> Dict:
        """
        Lista todas as instâncias
        """
        url = f"{self.base_url}/instance/fetchInstances"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    # ===== MÉTODOS DE ENVIO DE MENSAGENS =====
    
    def send_text_message(self, instance_name: str, number: str, text: str) -> Dict:
        """
        Envia mensagem de texto
        """
        url = f"{self.base_url}/message/sendText/{instance_name}"
        
        payload = {
            "number": number,
            "text": text
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            try:
                return response.json()
            except ValueError:
                return {'error': f'Resposta inválida da API: {response.text}'}
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                return {'error': f'{str(e)} - {e.response.text}'}
            return {'error': str(e)}
    
    def send_media_message(self, instance_name: str, number: str, media_url: str = None,
                          media_base64: str = None, media_type: str = 'image', 
                          caption: str = None, filename: str = None) -> Dict:
        """
        Envia mensagem com mídia (imagem, vídeo, documento, áudio)
        Suporta envio por URL ou Base64
        """
        # Selecionar endpoint baseado no tipo
        if media_type == 'audio':
            url = f"{self.base_url}/message/sendWhatsAppAudio/{instance_name}"
        else:
            url = f"{self.base_url}/message/sendMedia/{instance_name}"
        
        # Preparar mídia (URL ou Base64)
        media_content = media_url if media_url else media_base64
        
        # Se for base64 com data URI, remover o prefixo
        if media_content and media_content.startswith('data:'):
            # Extrair apenas o conteúdo base64, removendo "data:mime/type;base64,"
            media_content = media_content.split(',', 1)[1] if ',' in media_content else media_content
        
        # Construir payload baseado no tipo
        if media_type == 'audio':
            payload = {
                "number": number,
                "audioMessage": {
                    "audio": media_content
                }
            }
        elif media_type == 'sticker':
            payload = {
                "number": number,
                "options": {
                    "delay": 1200
                },
                "stickerMessage": {
                    "sticker": media_content
                }
            }
        else:
            # Para image, video e document - todos usam sendMedia
            payload = {
                "number": number,
                "mediatype": media_type,
                "media": media_content,
                "options": {
                    "delay": 1200
                }
            }
            if caption:
                payload["caption"] = caption
            if filename and media_type == 'document':
                payload["fileName"] = filename
        
        print(f"[API] ==================== ENVIANDO MÍDIA ====================")
        print(f"[API] Endpoint: {url}")
        print(f"[API] Número: {payload.get('number')}")
        print(f"[API] Tipo: {payload.get('mediatype', 'N/A')}")
        media_size = len(str(payload.get('media', '')))
        print(f"[API] Tamanho do base64: {media_size} bytes ({media_size / 1024 / 1024:.2f} MB)")
        print(f"[API] Caption: {caption[:50] if caption else 'N/A'}")
        print(f"[API] Payload keys: {list(payload.keys())}")
        
        # Ajustar timeout baseado no tamanho do arquivo
        timeout = 120 if media_size > 10000000 else 60  # 2 min para arquivos grandes
        print(f"[API] Timeout: {timeout}s")
        
        try:
            print(f"[API] Enviando request...")
            response = requests.post(url, json=payload, headers=self.headers, timeout=timeout)
            print(f"[API] Status code: {response.status_code}")
            
            if response.status_code == 500:
                print(f"[API ERRO 500] Response completo: {response.text}")
                return {'error': 'Erro interno da API Evolution. O arquivo pode estar em formato incompatível. Tente converter o vídeo para MP4 com codec H.264.'}
            
            print(f"[API] Response (primeiros 500 chars): {response.text[:500]}")
            response.raise_for_status()
            print(f"[API] ==================== SUCESSO ====================")

            
            try:
                return response.json()
            except ValueError:
                return {'error': f'Resposta inválida da API: {response.text}'}
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                error_msg = f'{str(e)} - {e.response.text}'
            print(f"[API ERRO] {error_msg}")
            return {'error': error_msg}
    
    def file_to_base64(self, file_path: str) -> str:
        """
        Converte arquivo para base64
        """
        with open(file_path, 'rb') as file:
            file_content = file.read()
            base64_content = base64.b64encode(file_content).decode('utf-8')
            
            # Detectar mimetype
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type:
                return f"data:{mime_type};base64,{base64_content}"
            return f"data:application/octet-stream;base64,{base64_content}"
    
    # ===== WEBHOOK N8N =====
    
    def send_to_n8n_webhook(self, instance_id: str, instance_name: str, contatos: list, arquivo_data: dict = None) -> Dict:
        """
        Envia dados de campanha para o webhook do n8n
        
        Args:
            instance_id (str): ID da instância
            instance_name (str): Nome da instância
            contatos (list): Lista de contatos com Telefone e Mensagem
            arquivo_data (dict): Dados do arquivo (nome, tipo, tamanho, base64)
        
        Returns:
            Dict: Resposta da API
        """
        webhook_url = "https://n8n.sumconnectia.tech/webhook/activeSender"
        
        payload = {
            "id_instancia": instance_id,
            "nome_instancia": instance_name,
            "contatos": contatos,
        }
        
        # Enviar dados do arquivo diretamente no payload
        if arquivo_data:
            payload["nome_arquivo"] = arquivo_data.get("nome")
            payload["tipo_arquivo"] = arquivo_data.get("tipo")
            payload["tamanho_arquivo"] = arquivo_data.get("tamanho")
            payload["base64"] = arquivo_data.get("base64")
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=30)
            response.raise_for_status()
            
            try:
                return response.json()
            except ValueError:
                return {'error': f'Resposta inválida do webhook: {response.text}'}
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                return {'error': f'{str(e)} - {e.response.text}'}
            return {'error': str(e)}

    def send_fb_message(self, number: str, text: str) -> Dict:
        """
        Envia mensagem diretamente via Facebook Graph API (WhatsApp Business API)
        """
        phone_number_id = settings.FB_WABA_PHONE_NUMBER_ID
        access_token = settings.FB_WABA_ACCESS_TOKEN
        url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": number,
            "type": "text",
            "text": {
                "body": text
            }
        }
        
        try:
            print(f"[DEBUG] Enviando mensagem direta via FB API: {number}")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            # Tentar parse do JSON mesmo se der erro para ver o detalhe da Meta
            try:
                result = response.json()
            except ValueError:
                result = {"error": response.text}
                
            response.raise_for_status()
            print(f"[DEBUG] ✓ Mensagem FB enviada com sucesso!")
            return result
            
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                error_msg = f"{str(e)} - {e.response.text}"
            print(f"[ERROR] Falha na FB API: {error_msg}")
            return {"error": error_msg}

    def send_chat_message_to_n8n(self, number: str, text: str) -> Dict:
        """
        Envia uma resposta manual do chat para o n8n
        """
        webhook_url = "https://n8n.sumconnectia.tech/webhook/chatReply"
        
        payload = {
            "contact_number": number,
            "text": text,
            "direction": "OUT"
        }
        
        try:
            print(f"[DEBUG] Enviando resposta do chat para n8n: {webhook_url}")
            response = requests.post(webhook_url, json=payload, timeout=30)
            response.raise_for_status()
            
            try:
                return response.json()
            except ValueError:
                # Se o n8n retornar apenas texto (ex: "OK")
                return {"status": "success", "message": response.text}
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                error_msg = f'{str(e)} - {e.response.text}'
            print(f"[ERROR] Falha ao enviar para n8n: {error_msg}")
            return {'error': error_msg}
