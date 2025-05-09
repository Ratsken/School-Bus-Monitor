from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.conf import settings

CustomUser = get_user_model()

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

# Assuming your models are in core.models
from core.models import Bus, BusLocation, Route, CustomUser, Student, Concern, Notification
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

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
    """
    API endpoints for viewing Buses.
    Admin users can view all buses. Drivers can view their assigned bus.
    Parents can view buses assigned to their children's routes.
    """
    queryset = Bus.objects.all()
    permission_classes = [IsAuthenticated]
    # serializer_class = BusSerializer # Uncomment and define if you create BusSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned buses based on user role.
        """
        user = self.request.user
        if user.role == 'admin':
            return Bus.objects.all()
        elif user.role == 'driver':
            return Bus.objects.filter(driver=user)
        elif user.role == 'parent':
            # Return buses assigned to the parent's children's routes
            child_routes = Route.objects.filter(students__parent=user).distinct()
            bus_ids = child_routes.values_list('bus__id', flat=True)
            return Bus.objects.filter(id__in=bus_ids).distinct()
        return Bus.objects.none() # No access for other roles


class BusTripViewSet(viewsets.ViewSet):
    """
    API endpoints for drivers to manage bus trips (start/stop) and post location updates.
    Requires the user to be a driver and assigned to the bus.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        bus = get_object_or_404(Bus, pk=pk)
        if request.user.role != 'driver' or bus.driver != request.user:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Logic to start the bus trip
        bus.status = 'active'
        bus.save()
        return Response({'status': f'Trip started for Bus {bus.bus_number}'})

    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        bus = get_object_or_404(Bus, pk=pk)
        if request.user.role != 'driver' or bus.driver != request.user:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Logic to stop the bus trip
        bus.status = 'inactive'
        bus.save()
        return Response({'status': f'Trip stopped for Bus {bus.bus_number}'})

    @action(detail=True, methods=['post'])
    def post_location(self, request, pk=None):
        """
        Posts the current location for the specified bus.
        Requires the user to be the assigned driver.
        """
        bus = get_object_or_404(Bus, pk=pk)
        # Add role check and driver assignment check
        if request.user.role != 'driver' or bus.driver != request.user:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        speed = request.data.get('speed') # Optional

        if latitude is not None and longitude is not None:
            BusLocation.objects.create(
                bus=bus,
                latitude=latitude,
                longitude=longitude,
                speed=speed
            )
            return Response({'status': 'location updated'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': 'Latitude and longitude are required.'}, status=status.HTTP_400_BAD_REQUEST)


class LiveBusLocationViewSet(viewsets.ViewSet):
    """API endpoint to get the latest locations of active buses relevant to the user."""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Returns the latest location for active buses relevant to the user's role."""
        user = request.user

        # Filter active buses based on user role
        if user.role == 'admin':
            active_buses = Bus.objects.filter(status='active')
        elif user.role == 'parent':
            child_routes = Route.objects.filter(students__parent=user).distinct()
            bus_ids = child_routes.values_list('bus__id', flat=True)
            active_buses = Bus.objects.filter(id__in=bus_ids, status='active')
        elif user.role == 'driver':
            try:
                active_buses = Bus.objects.filter(driver=user, status='active')
            except Bus.DoesNotExist:
                active_buses = Bus.objects.none()
        else:
            active_buses = Bus.objects.none()  # No access for other roles

        locations = []
        for bus in active_buses:
            latest_location = BusLocation.objects.filter(bus=bus).order_by('-timestamp').first()
            if latest_location:
                # Query the Route model to find the route associated with this bus
                route = Route.objects.filter(bus=bus).first()
                route_name = route.name if route else 'Unassigned'
                locations.append({
                    'bus_id': bus.id,
                    'bus_number': bus.bus_number,
                    'latitude': latest_location.latitude,
                    'longitude': latest_location.longitude,
                    'timestamp': latest_location.timestamp.isoformat(),
                    'speed': latest_location.speed,
                    'route_name': route_name
                })

        return Response(locations)

class RouteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for viewing Routes.
    """
    queryset = Route.objects.all()
    permission_classes = [IsAuthenticated]
    # serializer_class = RouteSerializer # Uncomment and define if you create RouteSerializer

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
    """
    Dashboard view displaying information based on user role.
    Requires user to be authenticated.
    """
    template_name = 'dashboard/index.html'
    login_url = reverse_lazy('core:login') # Redirect to login if not authenticated

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user_role'] = user.role

        # Fetch data based on role
        if user.role == 'admin':
            context['total_buses'] = Bus.objects.count()
            context['total_routes'] = Route.objects.count()
            context['total_students'] = Student.objects.count()
            context['recent_concerns'] = Concern.objects.order_by('-timestamp')[:5]
            # You might want to add counts for active buses, buses in maintenance, etc.
            context['active_buses_count'] = Bus.objects.filter(status='active').count()
            context['in_maintenance_buses_count'] = Bus.objects.filter(status='in_maintenance').count()
            context['open_concerns_count'] = Concern.objects.filter(status='open').count()


        elif user.role == 'parent':
            context['children'] = user.children.all()
            # Filter notifications for 'parent' group or 'all' group, and specifically for this user
            context['recent_notifications'] = Notification.objects.filter(recipient_group__in=['parent', 'all'], recipients=user).order_by('-timestamp')[:5]
            context['recent_concerns'] = Concern.objects.filter(raised_by=user).order_by('-timestamp')[:5]

        elif user.role == 'driver':
            try:
                context['assigned_bus'] = Bus.objects.get(driver=user)
                context['assigned_route'] = Route.objects.filter(bus=context['assigned_bus']).first()
            except Bus.DoesNotExist:
                context['assigned_bus'] = None
                context['assigned_route'] = None
            # Filter notifications for 'driver' group or 'all' group
            context['recent_notifications'] = Notification.objects.filter(recipient_group__in=['driver', 'all']).order_by('-timestamp')[:5]

        return context


class BusTrackingView(LoginRequiredMixin, TemplateView):
    """
    Bus Tracking view displaying a map with bus and school locations.
    Requires user to be authenticated.
    """
    template_name = 'dashboard/bus_tracking.html'
    login_url = reverse_lazy('core:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Filter buses based on user role for the list display
        if user.role == 'admin':
            context['buses'] = Bus.objects.filter(status='active')
        elif user.role == 'parent':
            child_routes = Route.objects.filter(students__parent=user).distinct()
            bus_ids = child_routes.values_list('bus__id', flat=True)
            context['buses'] = Bus.objects.filter(id__in=bus_ids, status='active')
        elif user.role == 'driver':
            try:
                context['buses'] = Bus.objects.filter(driver=user, status='active')
            except Bus.DoesNotExist:
                context['buses'] = Bus.objects.none()
        else:
            context['buses'] = Bus.objects.none()


        context['mapbox_access_token'] = settings.MAPBOX_ACCESS_TOKEN

        # School locations to be displayed on the map
        SCHOOL_LOCATIONS = {
            'main_campus': {'name': 'Main Campus', 'coords': (25.2048, 55.2708)},
            'branch_1': {'name': 'Branch 1', 'coords': (25.0764, 55.1324)},
            'branch_2': {'name': 'Branch 2', 'coords': (25.2676, 55.2927)}
        }
        # Convert coordinates to [lng, lat] for Mapbox
        context['school_locations'] = [
            {'name': loc['name'], 'lng': loc['coords'][1], 'lat': loc['coords'][0]}
            for loc in SCHOOL_LOCATIONS.values()
        ]

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

# DRF API views are moved to api/views.py