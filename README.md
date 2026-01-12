# InstaHunter 2.0

Sistema de Disparador de Mensagens usando Evolution API v2.3

## Funcionalidades

- ✅ Cadastro e gerenciamento de instâncias WhatsApp
- ✅ Integração completa com Evolution API
- ✅ Geração e exibição de QR Code para conexão
- ✅ Monitoramento de status das instâncias
- ✅ Configurações avançadas (webhook, rejeitar chamadas, etc.)
- ✅ Interface moderna com Bootstrap 5

## Requisitos

- Python 3.8+
- Django 4.2+
- Evolution API v2.3 instalada e configurada

## Instalação

1. Clone o repositório ou baixe os arquivos

2. Crie um ambiente virtual:
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Configure as variáveis de ambiente:

Edite o arquivo `instahunter/settings.py` e configure:
- `EVOLUTION_API_URL`: URL da sua Evolution API
- `EVOLUTION_API_KEY`: Chave de API global da Evolution API

Ou crie um arquivo `.env` na raiz do projeto:
```
EVOLUTION_API_URL=https://seu-dominio.com
EVOLUTION_API_KEY=sua-chave-api-global
```

6. Execute as migrações:
```bash
python manage.py makemigrations
python manage.py migrate
```

7. Crie um superusuário (opcional):
```bash
python manage.py createsuperuser
```

8. Execute o servidor:
```bash
python manage.py runserver
```

9. Acesse: http://localhost:8000

## Estrutura do Projeto

```
INSTAHUNTER 2.0/
├── instahunter/           # Configurações do projeto Django
│   ├── settings.py        # Configurações principais
│   ├── urls.py            # URLs principais
│   └── wsgi.py
├── instances/             # App de gerenciamento de instâncias
│   ├── models.py          # Modelos de dados
│   ├── views.py           # Views/Controllers
│   ├── forms.py           # Formulários
│   ├── services.py        # Integração com Evolution API
│   ├── urls.py            # URLs do app
│   └── admin.py           # Configuração do admin
├── templates/             # Templates HTML
│   ├── base.html          # Template base
│   └── instances/         # Templates do app instances
├── static/                # Arquivos estáticos
│   ├── css/
│   └── js/
├── manage.py              # Script de gerenciamento Django
└── requirements.txt       # Dependências Python
```

## Uso

### Criar uma Nova Instância

1. Acesse "Nova Instância" no menu
2. Preencha o formulário com:
   - Nome da instância (único)
   - Número WhatsApp (opcional)
   - Tipo de integração
   - Configurações desejadas
3. Clique em "Salvar Instância"

### Conectar uma Instância

1. Acesse a página de detalhes da instância
2. Clique em "Conectar / Gerar QR Code"
3. Escaneie o QR Code com seu WhatsApp
4. Aguarde a conexão ser estabelecida

### Enviar Mensagens

(Funcionalidade a ser implementada na próxima versão)

## API Evolution

Este projeto utiliza a Evolution API v2.3. Para mais informações:
https://www.postman.com/agenciadgcode/evolution-api/documentation/nm0wqgt/evolution-api-v2-3

## Próximas Funcionalidades

- [ ] Envio de mensagens individuais
- [ ] Envio de mensagens em massa
- [ ] Agendamento de mensagens
- [ ] Importação de contatos via CSV
- [ ] Relatórios e estatísticas
- [ ] Envio de mídias (imagens, vídeos, documentos)
- [ ] Templates de mensagens

## Suporte

Para problemas ou dúvidas, consulte a documentação da Evolution API ou abra uma issue no repositório.

## Licença

Este projeto é de código aberto e está disponível sob a licença MIT.
