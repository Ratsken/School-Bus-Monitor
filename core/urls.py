from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.admin_dashboard_view, name='admin_dashboard'),
    path('notifications/', views.user_notifications_view, name='user_notifications'),
    path('concerns/raise/', views.raise_concern_view, name='raise_concern'),
    path('concerns/', views.user_concerns_view, name='user_concerns'),
    path('driver/update-location/', views.driver_update_view, name='driver_update'),
]