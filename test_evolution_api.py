"""
Script de diagnóstico para Evolution API
Testa a conectividade e tenta vários endpoints
"""

import os
import sys
import django
import requests
from pprint import pprint

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instahunter.settings')
django.setup()

from django.conf import settings

class EvolutionAPIDiagnostics:
    def __init__(self):
        self.base_url = settings.EVOLUTION_API_URL
        self.api_key = settings.EVOLUTION_API_KEY
        self.headers = {
            'apikey': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def print_config(self):
        """Mostra configuração atual"""
        print("\n" + "="*60)
        print("CONFIGURAÇÃO ATUAL")
        print("="*60)
        print(f"URL Base: {self.base_url}")
        print(f"API Key (primeiros 20 chars): {self.api_key[:20]}...")
        print(f"Headers: {self.headers}")
    
    def test_connection(self):
        """Testa conectividade básica"""
        print("\n" + "="*60)
        print("TESTE 1: CONEXÃO BÁSICA")
        print("="*60)
        
        try:
            print(f"Fazendo ping para {self.base_url}...")
            response = requests.get(self.base_url, timeout=5)
            print(f"✓ URL acessível (Status: {response.status_code})")
        except requests.exceptions.Timeout:
            print(f"✗ Timeout - URL não responde em 5 segundos")
            return False
        except requests.exceptions.ConnectionError:
            print(f"✗ Erro de conexão - URL não é acessível")
            return False
        except Exception as e:
            print(f"✗ Erro: {str(e)}")
            return False
        
        return True
    
    def test_fetch_instances(self):
        """Testa endpoint de listar instâncias"""
        print("\n" + "="*60)
        print("TESTE 2: LISTAR INSTÂNCIAS")
        print("="*60)
        
        url = f"{self.base_url}/instance/fetchInstances"
        print(f"URL: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"Response: {response.text[:500]}")
            
            if response.status_code == 200:
                print("✓ Endpoint funcionando!")
                try:
                    data = response.json()
                    print(f"Instâncias encontradas: {len(data.get('instances', []))}")
                    return True
                except:
                    print("⚠ Resposta não é JSON")
                    return False
            else:
                print(f"✗ Status inesperado")
                return False
        except Exception as e:
            print(f"✗ Erro: {type(e).__name__}: {str(e)}")
            return False
    
    def test_create_instance(self, instance_name: str = "test-qr-diagnostics"):
        """Testa criação de instância"""
        print("\n" + "="*60)
        print("TESTE 3: CRIAR INSTÂNCIA")
        print("="*60)
        
        url = f"{self.base_url}/instance/create"
        payload = {
            "instanceName": instance_name,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS",
            "token": self.api_key,
        }
        
        print(f"URL: {url}")
        print(f"Payload: {payload}")
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:800]}")
            
            if response.status_code in [200, 201, 202]:
                print("✓ Instância criada!")
                try:
                    data = response.json()
                    print(f"Resposta JSON: {data}")
                    return instance_name, data
                except:
                    return instance_name, None
            else:
                print(f"✗ Erro ao criar instância")
                return None, None
        except Exception as e:
            print(f"✗ Erro: {type(e).__name__}: {str(e)}")
            return None, None
    
    def test_qr_endpoints(self, instance_name: str):
        """Testa vários endpoints de QR Code"""
        print("\n" + "="*60)
        print("TESTE 4: ENDPOINTS DE CONEXÃO/QR CODE")
        print("="*60)
        
        endpoints = [
            # Endpoint correto identificado
            (f"{self.base_url}/instance/connect/{instance_name}", 'POST'),
            (f"{self.base_url}/instance/connect/{instance_name}", 'GET'),
            # Alternativas
            (f"{self.base_url}/instance/qrcode/{instance_name}", 'GET'),
            (f"{self.base_url}/instances/{instance_name}/qrcode", 'GET'),
            (f"{self.base_url}/instance/{instance_name}/qrcode", 'GET'),
            (f"{self.base_url}/instances/{instance_name}/connect", 'POST'),
            (f"{self.base_url}/instance/{instance_name}/connect", 'GET'),
            (f"{self.base_url}/qrcode/{instance_name}", 'GET'),
        ]
        
        results = []
        for url, method in endpoints:
            print(f"\n[{method}] {url}")
            try:
                if method == 'GET':
                    response = requests.get(url, headers=self.headers, timeout=10)
                else:
                    response = requests.post(url, json={}, headers=self.headers, timeout=10)
                
                status = response.status_code
                success = status in [200, 201, 202]
                symbol = "✓" if success else "✗"
                
                print(f"  {symbol} Status: {status}")
                if response.text:
                    text_preview = response.text[:300]
                    print(f"  Response: {text_preview}")
                
                results.append({
                    'endpoint': url,
                    'method': method,
                    'status': status,
                    'success': success
                })
                
                if success:
                    print(f"  ✓✓✓ ENDPOINT FUNCIONANDO! ✓✓✓")
                
            except Exception as e:
                print(f"  ✗ Erro: {type(e).__name__}: {str(e)}")
                results.append({
                    'endpoint': url,
                    'method': method,
                    'status': 'error',
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def test_connection_state(self, instance_name: str):
        """Testa endpoint de status da instância"""
        print("\n" + "="*60)
        print("TESTE 5: STATUS DA INSTÂNCIA")
        print("="*60)
        
        url = f"{self.base_url}/instance/connectionState/{instance_name}"
        print(f"URL: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✓ Status obtido com sucesso!")
                return True
            else:
                print(f"✗ Erro ao obter status")
                return False
        except Exception as e:
            print(f"✗ Erro: {type(e).__name__}: {str(e)}")
            return False
    
    def run_full_diagnostic(self):
        """Executa diagnóstico completo"""
        print("\n\n")
        print("╔" + "="*58 + "╗")
        print("║" + " "*58 + "║")
        print("║" + "EVOLUTION API DIAGNOSTIC TOOL".center(58) + "║")
        print("║" + " "*58 + "║")
        print("╚" + "="*58 + "╝")
        
        self.print_config()
        
        # Teste 1: Conexão
        if not self.test_connection():
            print("\n❌ PAROU: Não há conectividade com a URL base")
            return
        
        # Teste 2: Fetch instances
        self.test_fetch_instances()
        
        # Teste 3: Criar instância
        instance_name, create_response = self.test_create_instance()
        
        if instance_name:
            # Teste 4: Testar QR endpoints
            results = self.test_qr_endpoints(instance_name)
            
            # Teste 5: Status da instância
            self.test_connection_state(instance_name)
            
            # Resumo
            print("\n" + "="*60)
            print("RESUMO DOS TESTES")
            print("="*60)
            
            working = [r for r in results if r['success']]
            if working:
                print(f"\n✓ Endpoints que funcionaram ({len(working)}):")
                for r in working:
                    print(f"  [{r['method']}] {r['endpoint']}")
            else:
                print(f"\n✗ Nenhum endpoint de QR funcionou!")
            
            failing = [r for r in results if not r['success']]
            if failing and len(failing) <= 5:
                print(f"\n✗ Endpoints com erro ({len(failing)}):")
                for r in failing:
                    status = r.get('status', r.get('error', 'Unknown'))
                    print(f"  [{r['method']}] {r['endpoint']} - Status: {status}")


if __name__ == '__main__':
    diag = EvolutionAPIDiagnostics()
    diag.run_full_diagnostic()
    
    print("\n\n")
    print("💡 DICAS:")
    print("  1. Verifique se a URL da Evolution API está correta em settings.py")
    print("  2. Verifique se a API Key está correta em settings.py")
    print("  3. Verifique se a Evolution API está rodando e acessível")
    print("  4. Verifique firewall/proxy que possa estar bloqueando conexões")
    print("  5. Se um endpoint funcionar, atualize a lógica em services.py para usar aquele primeiro")
