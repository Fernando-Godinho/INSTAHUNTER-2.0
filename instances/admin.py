from django.contrib import admin
from .models import Instance, Message

@admin.register(Instance)
class InstanceAdmin(admin.ModelAdmin):
    list_display = ('instance_name', 'integration_type', 'status', 'created_at', 'updated_at')
    list_filter = ('integration_type', 'status', 'created_at')
    search_fields = ('instance_name', 'number')
    readonly_fields = ('created_at', 'updated_at', 'instance_id')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message_type', 'status', 'instance', 'sent_at')
    list_filter = ('message_type', 'status', 'sent_at')
    search_fields = ('recipient', 'text_content')
    readonly_fields = ('sent_at', 'response_data')
