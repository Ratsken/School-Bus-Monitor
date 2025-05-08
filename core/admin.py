# apps/accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Bus, BusLocation, Concern, CustomUser, Notification, Route, Student
from import_export.admin import ImportExportModelAdmin
from import_export import resources

class CustomUserResource(resources.ModelResource):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
        import_id_fields = ['username']

@admin.register(CustomUser)
class CustomUserAdmin(ImportExportModelAdmin, UserAdmin):
    resource_class = CustomUserResource
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)

    # Add 'role' to fieldsets
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'phone_number')}),
    )
    # Add 'role' to add_fieldsets
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'phone_number')}),
    )

    # Control visibility based on permissions
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        # Allow access to the Accounts module if the user can view any user
        return request.user.has_perm('accounts.view_customuser')

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        # Allow viewing if user has the specific view permission
        return request.user.has_perm('accounts.view_customuser')

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.has_perm('accounts.add_customuser')

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        # Users can change their own profile, or if they have change permission
        if obj is not None and obj == request.user:
            return True # Users can always change their own profile
        return request.user.has_perm('accounts.change_customuser')

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.has_perm('accounts.delete_customuser')

class BusResource(resources.ModelResource):
    class Meta:
        model = Bus
        fields = ('id', 'bus_number', 'driver', 'capacity', 'status')
        import_id_fields = ['bus_number'] # Use bus_number as the identifier for updates/creation

@admin.register(Bus)
class BusAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = BusResource
    list_display = ('bus_number', 'driver', 'capacity', 'status')
    list_filter = ('driver', 'status')
    search_fields = ('bus_number', 'driver__username')
    list_editable = ('status',) # Allow editing status directly in the list view (with permission)

    # Control visibility based on permissions
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        # Allow access to the 'Buses' module in admin if the user has any bus-related permission
        return request.user.has_perm('buses.view_bus') or \
                request.user.has_perm('buses.add_bus') or \
                request.user.has_perm('buses.change_bus') or \
                request.user.has_perm('buses.delete_bus') or \
                request.user.has_perm('buses.can_assign_driver') or \
                request.user.has_perm('buses.can_update_maintenance_status')

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        # Allow viewing if user has the specific view permission
        if request.user.has_perm('buses.view_bus'):
            return True
        # Drivers can view their assigned bus
        if request.user.role == 'driver' and obj is not None and obj.driver == request.user:
            return True
        return False

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.has_perm('buses.add_bus')

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        # Drivers can only change the status of their assigned bus
        if request.user.role == 'driver' and obj is not None and obj.driver == request.user:
            return request.user.has_perm('buses.can_update_maintenance_status')
        return request.user.has_perm('buses.change_bus')

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.has_perm('buses.delete_bus')

class RouteResource(resources.ModelResource):
    class Meta:
        model = Route
        fields = ('id', 'name', 'bus', 'start_time', 'end_time')
        import_id_fields = ['name']

@admin.register(Route)
class RouteAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = RouteResource
    list_display = ('name', 'bus', 'start_time', 'end_time')
    list_filter = ('bus',)
    search_fields = ('name', 'bus__bus_number')

    # Control visibility based on permissions
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.has_perm('routes.view_route') or \
                request.user.has_perm('routes.add_route') or \
                request.user.has_perm('routes.change_route') or \
                request.user.has_perm('routes.delete_route') or \
                request.user.has_perm('routes.can_assign_bus_to_route')

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.has_perm('routes.view_route'):
            return True
        # Drivers can view their assigned route
        if request.user.role == 'driver' and obj is not None and obj.bus is not None and obj.bus.driver == request.user:
            return True
        # Parents can view their child's route
        if request.user.role == 'parent' and obj is not None and obj.students.filter(parent=request.user).exists():
            return True
        return False

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.has_perm('routes.add_route')

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.has_perm('routes.change_route')

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.has_perm('routes.delete_route')

class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        fields = ('id', 'first_name', 'last_name', 'parent', 'assigned_route', 'student_id')
        import_id_fields = ['student_id'] # Or a combination of fields

@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = StudentResource
    list_display = ('first_name', 'last_name', 'parent', 'assigned_route', 'student_id')
    list_filter = ('assigned_route', 'parent')
    search_fields = ('first_name', 'last_name', 'student_id', 'parent__username', 'assigned_route__name')

    # Control visibility based on permissions
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.has_perm('students.view_student') or \
                request.user.has_perm('students.add_student') or \
                request.user.has_perm('students.change_student') or \
                request.user.has_perm('students.delete_student') or \
                request.user.has_perm('students.can_assign_student_to_route') or \
                request.user.has_perm('students.can_view_student_details')

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.has_perm('students.view_student'):
            return True
        # Parents can view their own children's details
        if request.user.role == 'parent' and obj is not None and obj.parent == request.user:
            return True
        return False

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.has_perm('students.add_student')

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.has_perm('students.change_student')

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.has_perm('students.delete_student')

@admin.register(BusLocation)
class BusLocationAdmin(admin.ModelAdmin):
    list_display = ('bus', 'latitude', 'longitude', 'timestamp')
    list_filter = ('bus', 'timestamp')
    search_fields = ('bus__bus_number',)
    date_hierarchy = 'timestamp' # Add a date drilldown

    # Control visibility based on permissions
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.has_perm('tracking.view_bus_location') or \
                request.user.has_perm('tracking.can_submit_bus_location')

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.has_perm('tracking.view_bus_location'):
            return True
        # Parents can view location of their child's bus
        if request.user.role == 'parent' and obj is not None and obj.bus.assigned_route.students.filter(parent=request.user).exists():
            return True
        # Drivers can view locations for their assigned bus
        if request.user.role == 'driver' and obj is not None and obj.bus.driver == request.user:
            return True
        return False

    # Restrict add/change/delete permissions for location data, as it's primarily from drivers/API
    def has_add_permission(self, request):
        return request.user.is_superuser # Only superusers can manually add locations

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser # Only superusers can manually change locations

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser # Only superusers can manually delete locations


class NotificationResource(resources.ModelResource):
    class Meta:
        model = Notification
        fields = ('id', 'bus', 'sender', 'recipient_group', 'subject', 'message', 'timestamp', 'notification_type', 'sent_via', 'status', 'last_attempt', 'retry_count')
        # You might not want to import/export all fields, adjust as needed

@admin.register(Notification)
class NotificationAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = NotificationResource
    list_display = ('subject', 'notification_type', 'bus', 'sender', 'recipient_group', 'timestamp', 'sent_via', 'status')
    list_filter = ('notification_type', 'recipient_group', 'sent_via', 'status')
    search_fields = ('subject', 'message', 'bus__bus_number', 'sender__username')
    date_hierarchy = 'timestamp'
    filter_horizontal = ('recipients',) # Use horizontal filter for many-to-many recipients

    # Control visibility based on permissions
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.has_perm('communication.can_send_notification') or \
                request.user.has_perm('communication.can_view_notifications') or \
                request.user.has_perm('communication.can_view_all_concerns') or \
                request.user.has_perm('communication.can_manage_concerns')

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.has_perm('communication.can_view_notifications'):
            return True
        # Users can view notifications sent to them or their group
        if obj is not None and (obj.recipients.filter(id=request.user.id).exists() or obj.recipient_group == request.user.role):
            return True
        return False

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.has_perm('communication.can_send_notification')

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        # Only allow changing status/retry info if user has send permission
        if request.user.has_perm('communication.can_send_notification'):
            return True
        return False # Prevent others from changing notifications

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        # Only allow deleting if user has send permission
        return request.user.has_perm('communication.can_send_notification')


class ConcernResource(resources.ModelResource):
    class Meta:
        model = Concern
        fields = ('id', 'raised_by', 'bus', 'subject', 'description', 'timestamp', 'status', 'resolved_by', 'resolved_at', 'resolution_notes')
        # You might not want to import/export all fields, adjust as needed

@admin.register(Concern)
class ConcernAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ConcernResource
    list_display = ('subject', 'raised_by', 'bus', 'timestamp', 'status', 'resolved_by')
    list_filter = ('status', 'bus', 'raised_by')
    search_fields = ('subject', 'description', 'raised_by__username', 'bus__bus_number')
    date_hierarchy = 'timestamp'
    list_editable = ('status',) # Allow changing status in list view (with permission)

    # Control visibility based on permissions
    def has_module_permission(self, request):
        # Concerns module visibility is tied to communication module permissions
        return super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        # Users can view concerns they raised
        if obj is not None and obj.raised_by == request.user:
            return True
        # Users with 'can_view_all_concerns' permission can view all
        return request.user.has_perm('communication.can_view_all_concerns')

    def has_add_permission(self, request):
        # Any logged-in user can raise a concern
        return request.user.is_authenticated

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        # Users with 'can_manage_concerns' can change status/resolution
        return request.user.has_perm('communication.can_manage_concerns')

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        # Only users with 'can_manage_concerns' can delete concerns
        return request.user.has_perm('communication.can_manage_concerns')


