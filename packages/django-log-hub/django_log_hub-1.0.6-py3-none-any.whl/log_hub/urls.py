from django.urls import path
from . import views

app_name = 'log_hub'

urlpatterns = [
    path('', views.log_view, name='log_view'),
    path('change-language/', views.change_language, name='change_language'),
    path('clear-log/<str:log_file_name>/', views.clear_log, name='clear_log'),
    path('download-log/<str:log_file_name>/', views.download_log, name='download_log'),
    
    # Yeni özel loglama sistemi test URL'leri
    path('test-custom-logging/', views.test_custom_logging, name='test_custom_logging'),
    path('test-decorator-logging/', views.test_decorator_logging, name='test_decorator_logging'),
    path('test-dynamic-logging/', views.test_dynamic_logging, name='test_dynamic_logging'),
]
