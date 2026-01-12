import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instahunter.settings')
django.setup()

from instances.models import Instance

# Limpar todos os QR Codes
Instance.objects.all().update(qrcode_base64=None)
print("✅ Todos os QR Codes foram limpos!")
print(f"Total de instâncias: {Instance.objects.count()}")
