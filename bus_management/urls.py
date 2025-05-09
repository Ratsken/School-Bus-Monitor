# In your project's urls.py (e.g., bus_management/bus_management/urls.py)

from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Define schema view for drf-yasg
schema_view = get_schema_view(
    openapi.Info(
        title="School Bus Management API",
        default_version='v1',
        description="API for managing school buses, routes, users, and tracking.",
        terms_of_service="https://www.google.com/policies/terms/", # Replace with your terms
        contact=openapi.Contact(email="contact@your-school.com"), # Replace with your contact
        license=openapi.License(name="BSD License"), # Replace with your license
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include your app's urls.py which now contains both template views and API views via the router
    path('', include('core.urls', namespace='core')), # Assuming your app is named 'core'

    # Swagger UI and ReDoc URLs (using re_path for regex patterns)
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
