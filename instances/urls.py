from django.urls import path
from . import views

app_name = 'instances'

urlpatterns = [
    # Página inicial
    path('', views.index, name='index'),
    
    # CRUD de instâncias
    path('instances/', views.instance_list, name='instance_list'),
    path('instances/create/', views.instance_create, name='instance_create'),
    path('instances/<int:pk>/', views.instance_detail, name='instance_detail'),
    path('instances/<int:pk>/edit/', views.instance_edit, name='instance_edit'),
    path('instances/<int:pk>/delete/', views.instance_delete, name='instance_delete'),
    
    # Ações da API
    path('instances/<int:pk>/connect/', views.instance_connect, name='instance_connect'),
    path('instances/<int:pk>/disconnect/', views.instance_disconnect, name='instance_disconnect'),
    path('instances/<int:pk>/restart/', views.instance_restart, name='instance_restart'),
    path('instances/<int:pk>/status/', views.instance_status, name='instance_status'),
    
    # Mensagens
    path('messages/send/', views.message_send, name='message_send'),
    path('messages/bulk/', views.message_bulk, name='message_bulk'),
    path('messages/history/', views.message_history, name='message_history'),
    path('messages/clear-errors/', views.message_clear_errors, name='message_clear_errors'),
    
    # Campanhas
    path('campaigns/', views.campaign_history, name='campaign_history'),
    path('campaigns/<int:pk>/', views.campaign_detail, name='campaign_detail'),
    path('campaigns/<int:pk>/cancel/', views.campaign_cancel, name='campaign_cancel'),
]
