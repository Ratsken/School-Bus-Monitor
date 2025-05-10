# apps/accounts/models.py
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType

class School(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    latitude = models.FloatField(help_text="Geographical latitude for mapping")
    longitude = models.FloatField(help_text="Geographical longitude for mapping")
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    principal = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('superuser', 'Superuser'),
        ('admin', 'School Administrator'),
        ('driver', 'Driver'),
        ('parent', 'Parent'),
        ('staff', 'Staff'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='parent')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    school = models.ForeignKey(
        School, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='users'
    )

    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name="custom_user_set",
        related_query_name="custom_user",
    )

    def __str__(self):
        return f"{self.username} ({self.school.name if self.school else 'No School'})"

    class Meta:
        verbose_name = 'User'

class Bus(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('in_maintenance', 'In Maintenance'),
        ('out_of_commission', 'Out of Commission'),
        ('delayed', 'Delayed'),
    )
    bus_number = models.CharField(max_length=50, unique=True)
    driver = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_buses')
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='buses',
        null=True,
        blank=True
    )
    capacity = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    last_known_latitude = models.FloatField(null=True, blank=True)
    last_known_longitude = models.FloatField(null=True, blank=True)
    last_known_location_time = models.DateTimeField(null=True, blank=True)
    last_known_speed = models.FloatField(null=True, blank=True)  # ✅ Add this field
    last_known_heading = models.FloatField(null=True, blank=True)  # ✅ Add this field
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_due = models.DateField(null=True, blank=True)
    maintenance_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"{self.bus_number} ({self.school.name if self.school else 'No School'})"

    @property
    def current_location(self):
        if self.last_known_latitude and self.last_known_longitude:
            return {
                'lat': self.last_known_latitude,
                'lng': self.last_known_longitude,
                'timestamp': self.last_known_location_time
            }
        return None

    @property
    def route(self):
        return Route.objects.filter(bus=self).first()
    
    class Meta:
        verbose_name_plural = "Buses"
        permissions = [
            ("can_assign_driver", "Can assign a driver to a bus"),
            ("can_update_maintenance_status", "Can update bus maintenance status"),
        ]

class Route(models.Model):
    name = models.CharField(max_length=100)
    bus = models.OneToOneField(Bus, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_route')
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='routes',
        null=True,
        blank=True
    )
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    stops = models.JSONField(default=list, blank=True)  # For storing route waypoints

    def __str__(self):
        return f"{self.name} ({self.school.name if self.school else 'No School'})"

    class Meta:
        unique_together = ('name', 'school')
        permissions = [
            ("can_assign_bus_to_route", "Can assign a bus to a route"),
        ]

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    parent = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    assigned_route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='students',
        null=True,
        blank=True
    )
    student_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    grade_level = models.CharField(max_length=20, blank=True, null=True)
    home_address = models.TextField(blank=True, null=True)
    pickup_location = models.JSONField(null=True, blank=True)  # {lat: x, lng: y}

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.school.name if self.school else 'No School'})"

    class Meta:
        permissions = [
            ("can_assign_student_to_route", "Can assign a student to a route"),
            ("can_view_student_details", "Can view detailed student information"),
        ]

class BusLocation(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(default=now)
    speed = models.FloatField(null=True, blank=True)
    heading = models.FloatField(null=True, blank=True)  # Direction in degrees
    is_trip_start = models.BooleanField(default=False)  # Add this field
    is_trip_end = models.BooleanField(default=False)   # Add this field

    def __str__(self):
        return f"{self.bus.bus_number} at ({self.latitude}, {self.longitude})"

    class Meta:
        ordering = ['-timestamp']
        permissions = [
            ("can_view_bus_location", "Can view real-time bus locations"),
            ("can_submit_bus_location", "Can submit bus location data"),
        ]

class Notification(models.Model):
    TYPE_CHOICES = (
        ('alert', 'Alert'),
        ('info', 'Information'),
        ('maintenance', 'Maintenance Update'),
        ('delay', 'Delay Notification'),
    )
    CHANNEL_CHOICES = (
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('system', 'System Notification'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('in_progress', 'In Progress'), # Added for threading status
    )

    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    # Using recipient_group for broad targeting, or specific users/parents
    recipient_group = models.CharField(max_length=20, choices=CustomUser.ROLE_CHOICES, blank=True, null=True)
    recipients = models.ManyToManyField(CustomUser, related_name='received_notifications', blank=True) # For specific recipients

    subject = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    sent_via = models.CharField(max_length=50, choices=CHANNEL_CHOICES, default='system')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    last_attempt = models.DateTimeField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Notification: {self.subject} ({self.status})"

    class Meta:
        ordering = ['-timestamp']
        permissions = [
            ("can_send_notification", "Can send notifications to user groups"),
            ("can_view_notifications", "Can view sent and received notifications"),
        ]

class Concern(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    )
    raised_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='concerns_raised')
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True, blank=True, related_name='concerns')
    subject = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    resolved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='concerns_resolved')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Concern: {self.subject} ({self.status})"

    class Meta:
        ordering = ['-timestamp']
        permissions = [
            ("can_view_all_concerns", "Can view all raised concerns"),
            ("can_manage_concerns", "Can change status and resolve concerns"),
        ]

