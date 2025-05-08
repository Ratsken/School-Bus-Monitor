"""school_bus_monitoring URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from core.views import BusLocationAPIView, BusLocationHistoryAPIView

# Swagger/OpenAPI configuration
schema_view = get_schema_view(
    openapi.Info(
        title="School Bus Monitoring API",
        default_version='v1',
        description="API for real-time school bus tracking system",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@schoolbusmonitoring.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin URLs
    path('admin/', admin.site.urls),
    
    # API Endpoints
    path('api/', include([
        path('locations/', include([
            path('current/', BusLocationAPIView.as_view(), name='current-locations'),
            path('history/<int:bus_id>/', BusLocationHistoryAPIView.as_view(), name='location-history'),
        ])),
        path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    ])),
    
    # Documentation with login
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Authentication URLs (for Swagger)
    path('accounts/login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Core application URLs
    path('', include('core.urls')),
]

# Static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)