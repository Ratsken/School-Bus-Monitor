from datetime import timedelta
from django.http import HttpResponse
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Subquery, OuterRef, Q, Avg
from django.contrib.auth import get_user_model
from django.conf import settings

CustomUser = get_user_model()

from core.serializers import BusSerializer, RouteSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

# Assuming your models are in core.models
from core.models import Bus, BusLocation, Route, CustomUser, School, Student, Concern, Notification
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

def start_trip(request, bus_id):
    bus = Bus.objects.get(id=bus_id)
    BusLocation.objects.create(bus=bus, latitude=bus.last_known_latitude, longitude=bus.last_known_longitude, is_trip_start=True)
    return HttpResponse("Trip started")

def stop_trip(request, bus_id):
    bus = Bus.objects.get(id=bus_id)
    BusLocation.objects.create(bus=bus, latitude=bus.last_known_latitude, longitude=bus.last_known_longitude, is_trip_start=False)
    return HttpResponse("Trip stopped")

class SchoolListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = School
    template_name = 'management/school_list.html'
    context_object_name = 'schools'
    
    def test_func(self):
        return self.request.user.role == 'admin'

class SchoolCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = School
    fields = ['name', 'address', 'latitude', 'longitude', 'phone', 'email', 'principal', 'is_active']
    template_name = 'management/school_form.html'
    success_url = reverse_lazy('core:manage_schools')
    
    def test_func(self):
        return self.request.user.role == 'admin'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class SchoolUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = School
    fields = ['name', 'address', 'latitude', 'longitude', 'phone', 'email', 'principal', 'is_active']
    template_name = 'management/school_form.html'
    success_url = reverse_lazy('core:manage_schools')
    
    def test_func(self):
        return self.request.user.role == 'admin'

class SchoolDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = School
    template_name = 'management/school_confirm_delete.html'
    success_url = reverse_lazy('core:manage_schools')
    
    def test_func(self):
        return self.request.user.role == 'admin'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dependent_objects'] = {
            'Users': self.object.users.count(),
            'Buses': self.object.buses.count(),
            'Students': self.object.students.count()
        }
        return context

# Manage Users
class ManageUsersView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """View to display a list of all users."""
    model = CustomUser
    template_name = 'management/manage_users.html'
    context_object_name = 'users'

    def test_func(self):
        return self.request.user.role == 'admin'

class AddUserView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """View to add a new user."""
    model = CustomUser
    fields = ['username', 'first_name', 'last_name', 'email', 'role']
    template_name = 'management/add_user.html'
    success_url = reverse_lazy('core:manage_users')

    def test_func(self):
        return self.request.user.role == 'admin'

class EditUserView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View to edit an existing user."""
    model = CustomUser
    fields = ['username', 'first_name', 'last_name', 'email', 'role']
    template_name = 'management/edit_user.html'
    success_url = reverse_lazy('core:manage_users')

    def test_func(self):
        return self.request.user.role == 'admin'

class DeleteUserView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View to delete a user."""
    model = CustomUser
    template_name = 'management/delete_user.html'
    success_url = reverse_lazy('core:manage_users')

    def test_func(self):
        return self.request.user.role == 'admin'

# Manage Students
class ManageStudentsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """View to display a list of all students."""
    model = Student
    template_name = 'management/manage_students.html'
    context_object_name = 'students'

    def test_func(self):
        return self.request.user.role == 'admin'

class AddStudentView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """View to add a new student."""
    model = Student
    fields = ['first_name', 'last_name', 'student_id', 'parent', 'assigned_route']  # Use correct field names
    template_name = 'management/add_student.html'
    success_url = reverse_lazy('core:manage_students')

    def test_func(self):
        return self.request.user.role == 'admin'

class EditStudentView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View to edit an existing student."""
    model = Student
    fields = ['first_name', 'last_name', 'parent', 'assigned_route', 'student_id']  # Use correct field names
    template_name = 'management/edit_student.html'
    success_url = reverse_lazy('core:manage_students')

    def test_func(self):
        return self.request.user.role == 'admin'

    def test_func(self):
        return self.request.user.role == 'admin'

class DeleteStudentView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View to delete a student."""
    model = Student
    template_name = 'management/delete_student.html'
    success_url = reverse_lazy('core:manage_students')

    def test_func(self):
        return self.request.user.role == 'admin'

# Manage Buses
class ManageBusesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """View to display a list of all buses."""
    model = Bus
    template_name = 'management/manage_buses.html'
    context_object_name = 'buses'

    def test_func(self):
        return self.request.user.role == 'admin'

class AddBusView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """View to add a new bus."""
    model = Bus
    fields = ['bus_number', 'capacity', 'status', 'driver', 'route']
    template_name = 'management/add_bus.html'
    success_url = reverse_lazy('core:manage_buses')

    def test_func(self):
        return self.request.user.role == 'admin'

class EditBusView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View to edit an existing bus."""
    model = Bus
    fields = ['bus_number', 'driver', 'capacity', 'status']  # Remove 'route'
    template_name = 'management/edit_bus.html'
    success_url = reverse_lazy('core:manage_buses')

    def test_func(self):
        return self.request.user.role == 'admin'

class DeleteBusView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View to delete a bus."""
    model = Bus
    template_name = 'management/delete_bus.html'
    success_url = reverse_lazy('core:manage_buses')

    def test_func(self):
        return self.request.user.role == 'admin'

# Manage Routes
class ManageRoutesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """View to display a list of all routes."""
    model = Route
    template_name = 'management/manage_routes.html'
    context_object_name = 'routes'

    def test_func(self):
        return self.request.user.role == 'admin'

class AddRouteView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """View to add a new route."""
    model = Route
    fields = ['name', 'description', 'start_point', 'end_point', 'stops']
    template_name = 'management/add_route.html'
    success_url = reverse_lazy('core:manage_routes')

    def test_func(self):
        return self.request.user.role == 'admin'

class EditRouteView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View to edit an existing route."""
    model = Route
    fields = ['name', 'description', 'start_point', 'end_point', 'stops']
    template_name = 'management/edit_route.html'
    success_url = reverse_lazy('core:manage_routes')

    def test_func(self):
        return self.request.user.role == 'admin'

class DeleteRouteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View to delete a route."""
    model = Route
    template_name = 'management/delete_route.html'
    success_url = reverse_lazy('core:manage_routes')

    def test_func(self):
        return self.request.user.role == 'admin'

class BusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bus.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = BusSerializer  # Ensure it's included

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Bus.objects.all()
        elif user.role == 'driver':
            return Bus.objects.filter(driver=user)
        elif user.role == 'parent':
            child_routes = Route.objects.filter(students__parent=user).distinct()
            bus_ids = child_routes.values_list('bus__id', flat=True)
            return Bus.objects.filter(id__in=bus_ids).distinct()
        return Bus.objects.none()

class BusTripViewSet(viewsets.ViewSet):
    """Enhanced bus trip management with location history"""
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        bus = get_object_or_404(Bus, pk=pk)
        if request.user.role != 'driver' or bus.driver != request.user:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        bus.status = 'active'
        bus.save()
        
        # Create a trip start log
        BusLocation.objects.create(
            bus=bus,
            latitude=bus.last_known_latitude,
            longitude=bus.last_known_longitude,
            speed=0,
            is_trip_start=True
        )
        
        return Response({
            'status': f'Trip started for Bus {bus.bus_number}',
            'bus_status': bus.status
        })

    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        bus = get_object_or_404(Bus, pk=pk)
        if request.user.role != 'driver' or bus.driver != request.user:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        bus.status = 'inactive'
        bus.save()
        
        # Create a trip end log
        BusLocation.objects.create(
            bus=bus,
            latitude=bus.last_known_latitude,
            longitude=bus.last_known_longitude,
            speed=0,
            is_trip_end=True
        )
        
        return Response({
            'status': f'Trip stopped for Bus {bus.bus_number}',
            'bus_status': bus.status
        })

    @action(detail=True, methods=['post'])
    def post_location(self, request, pk=None):
        bus = get_object_or_404(Bus, pk=pk)
        if request.user.role != 'driver' or bus.driver != request.user:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        speed = request.data.get('speed', 0)

        if None in (latitude, longitude):
            return Response(
                {'detail': 'Latitude and longitude are required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update bus's last known location
        bus.last_known_latitude = latitude
        bus.last_known_longitude = longitude
        bus.last_known_location_time = timezone.now()
        bus.save()

        # Create location record
        location = BusLocation.objects.create(
            bus=bus,
            latitude=latitude,
            longitude=longitude,
            speed=speed
        )

        return Response({
            'status': 'Location updated',
            'timestamp': location.timestamp,
            'bus_status': bus.status
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def location_history(self, request, pk=None):
        bus = get_object_or_404(Bus, pk=pk)
        if request.user.role not in ['admin', 'driver'] or (
            request.user.role == 'driver' and bus.driver != request.user
        ):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Get locations from the last 24 hours by default
        hours = int(request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        
        locations = BusLocation.objects.filter(
            bus=bus,
            timestamp__gte=since
        ).order_by('-timestamp')

        return Response([{
            'latitude': loc.latitude,
            'longitude': loc.longitude,
            'timestamp': loc.timestamp,
            'speed': loc.speed,
            'is_trip_start': loc.is_trip_start,
            'is_trip_end': loc.is_trip_end
        } for loc in locations])

# views.py (updated LiveBusLocationViewSet)
class LiveBusLocationViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for live bus locations"""

    queryset = Bus.objects.all()
    serializer_class = BusSerializer  # Ensure data is properly serialized
    
    def list(self, request):
        user = request.user
        active_buses = Bus.objects.none()

        # Restrict buses based on user role
        if user.role == 'admin':
            active_buses = Bus.objects.all()
        elif user.role == 'parent':
            active_buses = Bus.objects.filter(route__students__parent=user).distinct()
        elif user.role == 'driver':
            active_buses = Bus.objects.filter(driver=user)

        # Get latest location per bus
        latest_locations = BusLocation.objects.filter(bus=OuterRef('pk')).order_by('-timestamp')

        # Update Bus model with latest known latitude, longitude, timestamp, speed, and heading
        Bus.objects.update(
            last_known_latitude=Subquery(latest_locations.values('latitude')[:1]),
            last_known_longitude=Subquery(latest_locations.values('longitude')[:1]),
            last_known_location_time=Subquery(latest_locations.values('timestamp')[:1]),
            last_known_speed=Subquery(latest_locations.values('speed')[:1]),
            last_known_heading=Subquery(latest_locations.values('heading')[:1])
        )

        # Remove older locations, keeping only the latest per bus
        BusLocation.objects.exclude(id__in=latest_locations.values('id')[:1]).delete()

        # Serialize updated bus data
        serializer = BusSerializer(active_buses, many=True)
        return Response(serializer.data)

class RouteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for viewing Routes.
    """
    queryset = Route.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = RouteSerializer # Uncomment and define if you create RouteSerializer

    def retrieve(self, request, pk=None):
        """
        Returns details for a specific route, including placeholder points.
        """
        route = get_object_or_404(Route, pk=pk)
        # You would typically fetch and format route points here
        # Example: Fetch points from route.points field (if it exists and is a JSONField)
        # route_points = route.points if hasattr(route, 'points') else []
        # Or if points are in a separate model:
        # route_points = list(route.route_points.values('latitude', 'longitude')) # Assuming a related_name 'route_points'

        return Response({'route_id': route.id, 'route_name': route.name, 'points': []}) # Replace [] with actual route points

# --- Registration and Authentication Views ---
class CustomLoginView(LoginView):
    """
    Custom Login View using a dedicated template.
    """
    template_name = 'registration/login.html'
    form_class = AuthenticationForm
    # Redirect to dashboard after successful login
    def get_success_url(self):
        return reverse_lazy('core:dashboard')

class CustomLogoutView(LogoutView):
    """
    Custom Logout View redirecting to the login page.
    """
    next_page = reverse_lazy('core:login')

class CustomRegisterView(CreateView):
    """
    Custom Registration View for creating new users.
    Requires a custom form to handle user creation and role assignment.
    """
    model = CustomUser
    # You MUST create a custom form for registration that handles roles and other fields
    # from .forms import CustomUserCreationForm # Example import
    # form_class = CustomUserCreationForm
    # Using basic fields for demonstration, replace with your form
    fields = ['username', 'email', 'password', 'role', 'first_name', 'last_name', 'phone_number']
    template_name = 'registration/register.html'
    success_url = reverse_lazy('core:login') # Redirect to login page after successful registration

    def form_valid(self, form):
        # Hash the password manually if not using a ModelForm with set_password
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form)

class CustomPasswordResetView(PasswordResetView):
    """
    Custom Password Reset View.
    """
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html' # Create this template
    success_url = reverse_lazy('core:password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    """
    Custom Password Reset Done View.
    """
    template_name = 'registration/password_reset_done.html' # Create this template

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Custom Password Reset Confirm View.
    """
    template_name = 'registration/password_reset_confirm.html' # Create this template
    success_url = reverse_lazy('core:password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """
    Custom Password Reset Complete View.
    """
    template_name = 'registration/password_reset_complete.html' # Create this template

# --- Dashboard and Management Views (Admin/Driver/Parent) ---
class DashboardView(LoginRequiredMixin, TemplateView):
    """Enhanced Dashboard with role-specific statistics
        Dashboard view displaying information based on user role.
        Requires user to be authenticated.
    """
    template_name = 'dashboard/index.html'
    login_url = reverse_lazy('core:login') # Redirect to login if not authenticated
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # School locations for map
        schools = School.objects.all()
        context['school_locations'] = [{
            'name': school.name,
            'lat': school.latitude,
            'lng': school.longitude,
            'address': school.address
        } for school in schools]
        
        # Bus data for map
        if user.role == 'admin':
            buses = Bus.objects.annotate(
                latest_location=Subquery(
                    BusLocation.objects.filter(bus=OuterRef('pk'))
                    .order_by('-timestamp')
                    .values('timestamp')[:1]
                )
            ).exclude(latest_location__isnull=True).order_by('-latest_location')[:10]
        elif user.role == 'parent':
            buses = Bus.objects.filter(
                assigned_route__students__parent=user
            ).exclude(
                Q(last_known_latitude__isnull=True) |
                Q(last_known_longitude__isnull=True)
            )
        elif user.role == 'driver':
            buses = Bus.objects.filter(driver=user)
        else:
            buses = Bus.objects.none()
            
        context['buses'] = [{
            'id': bus.id,
            'bus_number': bus.bus_number,
            'status': bus.status,
            'latitude': bus.last_known_latitude,
            'longitude': bus.last_known_longitude,
            'timestamp': bus.last_known_location_time,
            'route_name': bus.route.name if bus.route else None,
            'route_stops': bus.route.stops if bus.route else []
        } for bus in buses]
        
        # Role-specific statistics
        if user.role == 'admin':
            context.update(self._admin_statistics(user))
        elif user.role == 'parent':
            context.update(self._parent_statistics(user))
        elif user.role == 'driver':
            context.update(self._driver_statistics(user))
            
        return context    
    def _admin_statistics(self, user):
        from django.db.models import Count, Q, Subquery, OuterRef
        from datetime import datetime, timedelta
        from django.utils import timezone

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        return {
            'stats': {
                'total_buses': Bus.objects.count(),
                'active_buses': Bus.objects.filter(status='active').count(),
                'buses_in_maintenance': Bus.objects.filter(status='in_maintenance').count(),
                'total_routes': Route.objects.count(),
                'unassigned_routes': Route.objects.filter(bus__isnull=True).count(),
                'total_students': Student.objects.count(),
                'students_without_route': Student.objects.filter(assigned_route__isnull=True).count(),
                'open_concerns': Concern.objects.filter(status='open').count(),
                'today_notifications': Notification.objects.filter(
                    timestamp__gte=today_start
                ).count(),
            },
            'recent_activity': {
                'recent_concerns': Concern.objects.order_by('-timestamp')[:5],
                'recent_notifications': Notification.objects.order_by('-timestamp')[:5],
                'bus_status_changes': BusLocation.objects.filter(
                    # Adjust this filter to use existing fields or remove it
                    # Example: Q(speed__gt=0)  # Example condition
                ).order_by('-timestamp')[:5],
            },
            'map_buses': Bus.objects.annotate(
                latest_location=Subquery(
                    BusLocation.objects.filter(bus=OuterRef('pk'))
                    .order_by('-timestamp')
                    .values('timestamp')[:1]
                )
            ).exclude(latest_location__isnull=True).order_by('-latest_location')[:10]
        }
    
    def _parent_statistics(self, user):
        children = user.children.all()
        child_routes = Route.objects.filter(students__in=children).distinct()
        
        return {
            'children': children,
            'stats': {
                'active_buses': Bus.objects.filter(
                    assigned_route__in=child_routes,
                    status='active'
                ).count(),
                'delayed_buses': Bus.objects.filter(
                    assigned_route__in=child_routes,
                    status='delayed'
                ).count(),
                'child_routes': child_routes.count(),
            },
            'recent_activity': {
                'recent_notifications': Notification.objects.filter(
                    Q(recipient_group__in=['parent', 'all']) | Q(recipients=user)
                ).order_by('-timestamp')[:5],
                'recent_concerns': Concern.objects.filter(
                    raised_by=user
                ).order_by('-timestamp')[:5],
            },
            'map_buses': Bus.objects.filter(
                assigned_route__in=child_routes
            ).exclude(
                Q(last_known_latitude__isnull=True) |
                Q(last_known_longitude__isnull=True)
            ).select_related('assigned_route', 'driver')
        }
    
    def _driver_statistics(self, user):
        try:
            assigned_bus = Bus.objects.get(driver=user)
            route = assigned_bus.assigned_route
            
            # Get today's trip history
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_locations = BusLocation.objects.filter(
                bus=assigned_bus,
                timestamp__gte=today_start
            ).order_by('timestamp')
            
            return {
                'assigned_bus': assigned_bus,
                'assigned_route': route,
                'stats': {
                    'today_stops': today_locations.count(),
                    'average_speed': today_locations.aggregate(
                        avg_speed=Avg('speed')
                    )['avg_speed'] or 0,
                    'route_stops': len(route.stops) if route and hasattr(route, 'stops') else 0,
                    'last_update': assigned_bus.last_known_location_time,
                },
                'recent_activity': {
                    'recent_notifications': Notification.objects.filter(
                        Q(recipient_group__in=['driver', 'all'])
                    ).order_by('-timestamp')[:5],
                    'today_trips': BusLocation.objects.filter(
                        bus=assigned_bus,
                        timestamp__gte=today_start,
                        is_trip_start=True
                    ).count(),
                },
                'map_buses': Bus.objects.filter(
                    driver=user
                ).annotate(
                    latest_location=Subquery(
                        BusLocation.objects.filter(bus=OuterRef('pk'))
                        .order_by('-timestamp')
                        .values('timestamp')[:1]
                    )
                ).exclude(latest_location__isnull=True)
            }
        except Bus.DoesNotExist:
            return {
                'assigned_bus': None,
                'assigned_route': None,
                'stats': {},
                'recent_activity': {},
                'map_buses': Bus.objects.none()
            }

class BusTrackingView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/bus_tracking.html'
    login_url = reverse_lazy('core:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # School locations for map
        schools = School.objects.all()
        context['school_locations'] = [{
            'name': school.name,
            'lat': school.latitude,
            'lng': school.longitude,
            'address': school.address
        } for school in schools]

        # Bus data for map
        if user.role == 'admin':
            buses = Bus.objects.all()
        elif user.role == 'parent':
            buses = Bus.objects.filter(
                assigned_route__students__parent=user
            )
        elif user.role == 'driver':
            buses = Bus.objects.filter(driver=user)
        else:
            buses = Bus.objects.none()

        context['buses'] = []
        for bus in buses:
            latest_location = BusLocation.objects.filter(bus=bus).order_by('-timestamp').first()
            if latest_location:
                context['buses'].append({
                    'id': bus.id,
                    'bus_number': bus.bus_number,
                    'status': bus.status,
                    'latitude': latest_location.latitude,
                    'longitude': latest_location.longitude,
                    'timestamp': latest_location.timestamp,
                    'route_name': bus.route.name if bus.route else 'Unassigned',
                    'route_stops': bus.route.stops if bus.route else []
                })

        return context

# --- Communication Views ---
class UserNotificationsView(LoginRequiredMixin, TemplateView):
    """
    View to display notifications for the authenticated user.
    """
    template_name = 'communication/user_notifications.html'
    login_url = reverse_lazy('core:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.role == 'admin':
            context['notifications'] = Notification.objects.all().order_by('-timestamp')
        else:
            # Filter notifications relevant to the user's role or specific user
            # Assuming 'all' group exists and recipients is a ManyToManyField
            context['notifications'] = Notification.objects.filter(recipient_group__in=['all', user.role], recipients=user).order_by('-timestamp')
        return context

class RaiseConcernView(LoginRequiredMixin, CreateView):
    """
    View to allow authenticated users to raise a concern.
    Requires a form for concern creation.
    """
    model = Concern
    fields = ['bus', 'subject', 'description']  # Basic fields, customize as needed
    template_name = 'communication/raise_concern.html'
    success_url = reverse_lazy('core:user_concerns')  # Use namespace if app_name is defined
    login_url = reverse_lazy('core:login')

    def form_valid(self, form):
        form.instance.raised_by = self.request.user
        return super().form_valid(form)

class UserConcernsView(LoginRequiredMixin, TemplateView):
    """
    View to display concerns raised by or relevant to the authenticated user.
    """
    template_name = 'communication/user_concerns.html'
    login_url = reverse_lazy('core:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.role == 'admin':
            context['concerns'] = Concern.objects.all().order_by('-timestamp')
        else:
            context['concerns'] = Concern.objects.filter(raised_by=user).order_by('-timestamp')
        return context
