#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instahunter.settings')
django.setup()

from instances.models import Instance

inst = Instance.objects.get(pk=11)
print(f"Instância: {inst.instance_name}")
print(f"Status: {inst.status}")
print(f"QR Code Base64: {'SIM' if inst.qrcode_base64 else 'NÃO'}")
if inst.qrcode_base64:
    print(f"Começa com: {inst.qrcode_base64[:50]}...")
    print(f"Tamanho: {len(inst.qrcode_base64)}")
else:
    print("QR Code vazio!")
