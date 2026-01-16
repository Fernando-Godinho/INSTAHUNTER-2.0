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
        Conecta uma instância (gera QR Code)
        Tenta vários endpoints até encontrar o correto
        """
        # Primeiro, verificar se a instância existe
        status_check = self.get_instance_status(instance_name)
        if 'error' in status_check:
            print(f"[DEBUG] Instância '{instance_name}' não existe na API: {status_check['error']}")
            return {'error': f"Instância não existe na API: {status_check['error']}"}
        
        print(f"[DEBUG] Status check bem-sucedido: {status_check}")
        
        # Lista de endpoints a tentar (em ordem de preferência)
        endpoints = [
            (f"{self.base_url}/instance/qrcode/{instance_name}", 'GET', {}),
            (f"{self.base_url}/instances/{instance_name}/qrcode", 'GET', {}),
            (f"{self.base_url}/instance/{instance_name}/qrcode", 'GET', {}),
            (f"{self.base_url}/instance/connect/{instance_name}", 'POST', {'number': number} if number else {}),
            (f"{self.base_url}/instance/{instance_name}/connect", 'GET', {}),
        ]
        
        for url, method, payload in endpoints:
            print(f"\n[DEBUG] ========================================")
            print(f"[DEBUG] Tentando {method} - URL: {url}")
            print(f"[DEBUG] Payload: {payload if payload else 'Nenhum'}")
            
            try:
                if method == 'GET':
                    response = requests.get(url, headers=self.headers, timeout=30)
                else:
                    response = requests.post(url, json=payload if payload else {}, headers=self.headers, timeout=30)
                
                print(f"[DEBUG] Status Code: {response.status_code}")
                print(f"[DEBUG] Headers: {dict(response.headers)}")
                print(f"[DEBUG] Response: {response.text[:500]}")  # Primeiros 500 chars
                
                # Aceitar 200, 201, 202 como sucesso
                if response.status_code in [200, 201, 202]:
                    try:
                        result = response.json()
                        print(f"[DEBUG] ✓ SUCESSO! Endpoint funcionou: {url}")
                        return result
                    except:
                        print(f"[DEBUG] ✗ Resposta não é JSON válido")
                        continue
                else:
                    print(f"[DEBUG] ✗ Status {response.status_code}, tentando próximo endpoint...")
                    
            except requests.exceptions.RequestException as e:
                print(f"[DEBUG] ✗ Exceção RequestException: {type(e).__name__}")
                print(f"[DEBUG] Mensagem: {str(e)}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"[DEBUG] Resposta de erro: {e.response.text[:500]}")
                continue
            except Exception as e:
                print(f"[DEBUG] ✗ Erro inesperado: {type(e).__name__}: {str(e)}")
                continue
        
        print(f"\n[DEBUG] ========================================")
        print(f"[DEBUG] ✗ FALHA TOTAL: Nenhum endpoint funcionou!")
        print(f"[DEBUG] URL Base: {self.base_url}")
        print(f"[DEBUG] Nome da instância: {instance_name}")
        print(f"[DEBUG] Headers enviados: {self.headers}")
        print(f"[DEBUG] ========================================\n")
        
        # Se nenhum endpoint funcionou
        return {'error': 'Nenhum endpoint para gerar QR Code funcionou. Verifique os logs acima para detalhes.'}
    
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
