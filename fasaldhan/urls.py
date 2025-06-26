from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def root_view(request):
    """Simple root view for testing"""
    return JsonResponse({
        'message': 'Fasaldhan Backend API is running!',
        'available_endpoints': {
            'api_overview': '/api/overview/',
            'admin': '/admin/',
            'user_auth': '/api/auth/',
            'contract_system': '/api/contract/',
            'register': '/api/auth/register/',
            'login': '/api/auth/login/',
        }
    })

urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),
    path('api/', include('rest_framework.urls')),  # DRF browsable API
    path('api/', include('user.urls')),  # User app URLs
    path('api/contract/', include('contract.urls')),  # Contract app URLs
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)