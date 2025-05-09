# In your app's urls.py (e.g., core/urls.py)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views # Your existing views for templates

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'buses', views.BusViewSet, basename='bus') # Provides list and detail for buses
router.register(r'bus-trips', views.BusTripViewSet, basename='bus-trip') # Provides start/stop/post_location actions for buses
router.register(r'live-bus-locations', views.LiveBusLocationViewSet, basename='live-bus-location') # Provides list of live locations
router.register(r'routes', views.RouteViewSet, basename='route') # Provides list and detail for routes

# You would register other ViewSets here (User, Student, Concern, Notification)
# router.register(r'users', api_views.UserViewSet, basename='user')
# router.register(r'students', api_views.StudentViewSet, basename='student')
# router.register(r'concerns', api_views.ConcernViewSet, basename='concern')
# router.register(r'notifications', api_views.NotificationViewSet, basename='notification')
app_name = 'core'  # Namespace for the app

# Define your URL patterns

urlpatterns = [
    # Authentication URLs (using your existing views)
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.CustomRegisterView.as_view(), name='register'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Dashboard and Management URLs (using your existing views)
    path('', views.DashboardView.as_view(), name='dashboard'), # Homepage can be the dashboard after login
    path('bus-tracking/', views.BusTrackingView.as_view(), name='bus_tracking'),

    # Manage Users
    path('manage-users/', views.ManageUsersView.as_view(), name='manage_users'),
    path('manage-users/add/', views.AddUserView.as_view(), name='add_user'),
    path('manage-users/edit/<int:pk>/', views.EditUserView.as_view(), name='edit_user'),
    path('manage-users/delete/<int:pk>/', views.DeleteUserView.as_view(), name='delete_user'),

    # Manage Students
    path('manage-students/', views.ManageStudentsView.as_view(), name='manage_students'),
    path('manage-students/add/', views.AddStudentView.as_view(), name='add_student'),
    path('manage-students/edit/<int:pk>/', views.EditStudentView.as_view(), name='edit_student'),
    path('manage-students/delete/<int:pk>/', views.DeleteStudentView.as_view(), name='delete_student'),

    # Manage Buses
    path('manage-buses/', views.ManageBusesView.as_view(), name='manage_buses'),
    path('manage-buses/add/', views.AddBusView.as_view(), name='add_bus'),
    path('manage-buses/edit/<int:pk>/', views.EditBusView.as_view(), name='edit_bus'),
    path('manage-buses/delete/<int:pk>/', views.DeleteBusView.as_view(), name='delete_bus'),

    # Manage Routes
    path('manage-routes/', views.ManageRoutesView.as_view(), name='manage_routes'),
    path('manage-routes/add/', views.AddRouteView.as_view(), name='add_route'),
    path('manage-routes/edit/<int:pk>/', views.EditRouteView.as_view(), name='edit_route'),
    path('manage-routes/delete/<int:pk>/', views.DeleteRouteView.as_view(), name='delete_route'),
    
    # Communication URLs (using your existing views)
    path('notifications/', views.UserNotificationsView.as_view(), name='user_notifications'),
    path('concerns/raise/', views.RaiseConcernView.as_view(), name='raise_concern'),
    path('concerns/', views.UserConcernsView.as_view(), name='user_concerns'),

    # API URLs (using DRF Router)
    path('api/', include(router.urls)),
]
