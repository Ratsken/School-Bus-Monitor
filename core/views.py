# core/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from .models import Bus, Notification, Route, Student, CustomUser, Concern
from django.utils import timezone
from django.db import models
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.cache import cache
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ConcernForm
from django.core.mail import send_mail
from django.conf import settings
import threading
from tenacity import retry, stop_after_attempt, wait_exponential
import requests
import redis
import json
from datetime import datetime, timedelta

# Redis connection
r = redis.Redis.from_url(settings.CACHES['default']['LOCATION'])

@login_required
def driver_update_view(request):
    """View for drivers to update their bus location"""
    if request.user.role != 'driver':
        messages.error(request, "Only drivers can access this page")
        return redirect('admin_dashboard')
    
    # Get the buses assigned to this driver
    assigned_buses = request.user.assigned_buses.all()
    
    context = {
        'site_title': 'Update Bus Location',
        'assigned_buses': assigned_buses,
    }
    return render(request, 'dashboard/driver_update.html', context)

class BusLocationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current locations of all buses"""
        locations = []
        for bus in Bus.objects.filter(status='active'):
            location_data = r.get(f'bus:{bus.id}:location')
            if location_data:
                location = json.loads(location_data)
                locations.append({
                    'bus_id': bus.id,
                    'bus_number': bus.bus_number,
                    'latitude': location['lat'],
                    'longitude': location['lng'],
                    'speed': location.get('speed', 0),
                    'timestamp': location['timestamp']
                })
        return Response(locations)

    def post(self, request):
        """Update current bus location (for drivers)"""
        if request.user.role != 'driver':
            return Response(
                {'error': 'Only drivers can update locations'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        bus_id = request.data.get('bus_id')
        lat = request.data.get('latitude')
        lng = request.data.get('longitude')
        speed = request.data.get('speed', 0)
        
        if not all([bus_id, lat, lng]):
            return Response(
                {'error': 'Missing required parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        bus = Bus.objects.filter(id=bus_id, driver=request.user).first()
        if not bus:
            return Response(
                {'error': 'Bus not found or unauthorized'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        location_data = {
            'lat': lat,
            'lng': lng,
            'speed': speed,
            'timestamp': timezone.now().isoformat(),
            'bus_id': bus_id
        }
        
        r.set(f'bus:{bus_id}:location', json.dumps(location_data))
        r.lpush(f'bus:{bus_id}:history', json.dumps(location_data))
        r.ltrim(f'bus:{bus_id}:history', 0, 99)
        
        return Response({'status': 'success'})

class BusLocationHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, bus_id):
        """Get location history for a specific bus"""
        bus = Bus.objects.filter(id=bus_id).first()
        if not bus:
            return Response(
                {'error': 'Bus not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        if request.user.role not in ['admin', 'driver'] and (
            request.user.role == 'parent' and 
            not bus.students.filter(parent=request.user).exists()
        ):
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        history = r.lrange(f'bus:{bus_id}:history', 0, -1)
        locations = [json.loads(point) for point in history]
        
        return Response(locations)
    
@staff_member_required
def admin_dashboard_view(request):
    """Admin dashboard with cached system statistics and real-time bus locations."""
    cache_keys = {
        'total_buses': ('total_buses', 60 * 15),
        'active_routes': ('active_routes', 60 * 15),
        'total_students': ('total_students', 60 * 15),
        'online_drivers': ('online_drivers', 60 * 5)
    }
    
    context_data = {}
    for key, (cache_key, timeout) in cache_keys.items():
        cached_value = cache.get(cache_key)
        if cached_value is None:
            cached_value = {
                'total_buses': Bus.objects.count(),
                'active_routes': Route.objects.filter(bus__status='active').count(),
                'total_students': Student.objects.count(),
                'online_drivers': CustomUser.objects.filter(
                    role='driver', 
                    last_login__gte=timezone.now()-timedelta(minutes=15)
                ).count()
            }.get(key, 0)
            cache.set(cache_key, cached_value, timeout)
        context_data[key] = cached_value

    # Fetch bus locations from Redis
    bus_locations = []
    for bus in Bus.objects.filter(status='active'):
        location_data = r.get(f'bus:{bus.id}:location')
        if location_data:
            location = json.loads(location_data)
            bus_locations.append({
                'bus_number': bus.bus_number,
                'lat': location['lat'],
                'lng': location['lng'],
                'timestamp': location['timestamp'],
                'speed': location.get('speed', 0),
                'status': bus.status
            })

    context = {
        'site_title': 'School Bus Monitor',
        **context_data,
        'bus_locations': bus_locations,
        'MAPBOX_ACCESS_TOKEN': settings.MAPBOX_ACCESS_TOKEN,
        'recent_concerns': Concern.objects.order_by('-timestamp')[:5],
        'map_center': {'lat': 25.2048, 'lng': 55.2708},  # Default UAE coordinates
        'map_zoom': 10,
    }
    return render(request, 'dashboard/index.html', context)

@login_required
def bus_tracking_view(request, bus_id):
    """Retrieve bus tracking details including current location and last 24-hour history."""
    bus = get_object_or_404(Bus, id=bus_id)

    # Fetch location history (last 24 hours)
    location_history = [json.loads(data) for data in r.lrange(f'bus:{bus.id}:history', 0, -1)]
    
    # Get current location
    current_location = r.get(f'bus:{bus.id}:location')
    if current_location:
        current_location = json.loads(current_location)

    context = {
        'bus': bus,
        'current_location': current_location,
        'location_history': location_history,
        'site_title': f'Tracking Bus {bus.bus_number}',
    }
    return render(request, 'dashboard/bus_tracking.html', context)

@login_required
def update_bus_location(request):
    """Update bus location in Redis with live tracking."""
    if request.method == 'POST' and request.user.role == 'driver':
        try:
            data = json.loads(request.body)
            bus_id = data.get('bus_id')
            lat, lng = data.get('lat'), data.get('lng')
            speed = data.get('speed', 0)

            if not all([bus_id, lat, lng]):
                return JsonResponse({'status': 'error', 'message': 'Missing required data'}, status=400)

            # Verify driver owns the bus
            bus = Bus.objects.filter(id=bus_id, driver=request.user).first()
            if not bus:
                return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

            # Store location data
            location_data = {
                'lat': lat,
                'lng': lng,
                'speed': speed,
                'timestamp': timezone.now().isoformat(),
                'bus_id': bus_id
            }
            r.set(f'bus:{bus_id}:location', json.dumps(location_data))

            # Add to history, keeping last 100 entries
            r.lpush(f'bus:{bus_id}:history', json.dumps(location_data))
            r.ltrim(f'bus:{bus_id}:history', 0, 99)

            return JsonResponse({'status': 'success'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
# Use tenacity for retries within the threaded function
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def _send_single_notification(notification_id, channel):
    """Attempts to send a single notification via a specific channel."""
    from .models import Notification # Import inside function to avoid issues

    try:
        notification = Notification.objects.get(id=notification_id)

        if notification.status == 'sent':
            print(f"Notification {notification_id} already sent. Skipping.")
            return

        print(f"Attempting to send notification {notification_id} via {channel}, attempt {notification.retry_count + 1}")

        if channel == 'email':
            # Get recipients for email
            recipient_emails = [user.email for user in notification.recipients.all() if user.email]
            if notification.recipient_group:
                    # Add users from the recipient group
                    group_users = notification.recipient_group # This is the role string
                    recipient_emails.extend([user.email for user in settings.AUTH_USER_MODEL.objects.filter(role=group_users) if user.email])
            recipient_emails = list(set(recipient_emails)) # Remove duplicates

            if not recipient_emails:
                print(f"No valid email recipients for notification {notification_id}.")
                notification.status = 'failed'
                notification.save()
                return

            send_mail(
                notification.subject,
                notification.message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_emails,
                fail_silently=False, # Let exceptions raise for tenacity
            )
            print(f"Email sent for notification {notification_id}.")

        elif channel == 'sms':
            # Get recipients for SMS (users with phone numbers)
            recipient_phone_numbers = [user.phone_number for user in notification.recipients.all() if user.phone_number]
            if notification.recipient_group:
                    # Add users from the recipient group
                    group_users = notification.recipient_group
                    recipient_phone_numbers.extend([user.phone_number for user in settings.AUTH_USER_MODEL.objects.filter(role=group_users) if user.phone_number])
            recipient_phone_numbers = list(set(recipient_phone_numbers)) # Remove duplicates

            if not recipient_phone_numbers:
                print(f"No valid SMS recipients for notification {notification_id}.")
                notification.status = 'failed'
                notification.save()
                return

            # --- Placeholder for SMS Gateway API Call ---
            # Replace with actual API call to Twilio, Nexmo, etc.
            print(f"Simulating SMS send to {recipient_phone_numbers} for notification {notification_id}...")
            # Example using requests (requires a real SMS API endpoint)
            # try:
            #     response = requests.post(
            #         'YOUR_SMS_GATEWAY_API_URL',
            #         json={
            #             'to': recipient_phone_numbers,
            #             'message': notification.message,
            #             'from': settings.SMS_FROM_NUMBER,
            #             'apiKey': settings.SMS_GATEWAY_API_KEY,
            #             'apiSecret': settings.SMS_GATEWAY_API_SECRET,
            #         }
            #     )
            #     response.raise_for_status() # Raise an exception for bad status codes
            #     print(f"SMS sent successfully for notification {notification_id}.")
            # except requests.exceptions.RequestException as e:
            #     print(f"SMS sending failed for notification {notification_id}: {e}")
            #     raise # Re-raise to trigger tenacity retry

            # Simulate success or failure for demonstration
            import random
            if random.random() < 0.8: # 80% success rate
                print(f"SMS sent successfully for notification {notification_id} (simulated).")
            else:
                raise Exception("Simulated SMS sending failure") # Raise to trigger retry
            # --- End Placeholder ---


        elif channel == 'system':
            # For system notifications, you would typically use Django Channels
            # to push updates to connected users via WebSockets.
            # This requires a Channels setup (asgi.py, consumers.py, routing.py).
            # As Channels is not requested, we'll just mark it as sent for now.
            print(f"Simulating system notification for notification {notification_id}.")
            pass # Implement Channels logic here

        # If sending was successful (no exception raised by tenacity)
        notification.status = 'sent'
        notification.save()
        print(f"Notification {notification_id} status updated to sent.")

    except Notification.DoesNotExist:
        print(f"Notification with id {notification_id} not found during sending.")
    except Exception as e:
        # This exception will be caught by tenacity for retries
        print(f"Error sending notification {notification_id} via {channel}: {e}")
        notification = Notification.objects.get(id=notification_id) # Re-fetch to update status
        notification.retry_count += 1
        notification.last_attempt = timezone.now()
        if notification.retry_count >= 3: # Match tenacity stop_after_attempt
            notification.status = 'failed'
        else:
            notification.status = 'in_progress' # Keep trying
        notification.save()
        print(f"Notification {notification_id} status updated to {notification.status}, retry count {notification.retry_count}.")
        raise # Re-raise to allow tenacity to handle retries

def send_notification_async(notification_id):
    """Starts a new thread to send a notification."""
    # Fetch notification to determine channel(s)
    try:
        notification = Notification.objects.get(id=notification_id)
        channel = notification.sent_via

        # Create and start the thread
        thread = threading.Thread(target=_send_single_notification, args=(notification_id, channel))
        thread.start()
        print(f"Started thread for notification {notification_id} via {channel}.")

    except Notification.DoesNotExist:
        print(f"Notification with id {notification_id} not found for async sending.")
    except Exception as e:
        print(f"Error starting thread for notification {notification_id}: {e}")


# --- Views for Users ---

@login_required
def user_notifications_view(request):
    user_notifications = Notification.objects.filter(
        Q(recipients=request.user) | Q(recipient_group=request.user.role)
    ).distinct().order_by('-timestamp')

    context = {
        'notifications': user_notifications,
        'site_title': 'My Notifications',
    }
    return render(request, 'communication/user_notifications.html', context)

@login_required
def raise_concern_view(request):
    if request.method == 'POST':
        form = ConcernForm(request.POST)
        if form.is_valid():
            concern = form.save(commit=False)
            concern.raised_by = request.user
            concern.status = 'open'
            concern.save()
            
            # Send notification to admins
            notification = Notification.objects.create(
                subject=f"New Concern: {concern.subject}",
                message=f"{request.user.username} raised a concern: {concern.description}",
                notification_type='alert',
                recipient_group='admin',
                sent_via='system'
            )
            send_notification_async(notification.id)
            
            messages.success(request, 'Your concern has been submitted.')
            return redirect('user_concerns')
    else:
        form = ConcernForm()

    context = {
        'form': form,
        'site_title': 'Raise a Concern',
    }
    return render(request, 'communication/raise_concern.html', context)

@login_required
def user_concerns_view(request):
    user_concerns = Concern.objects.filter(raised_by=request.user).order_by('-timestamp')
    
    context = {
        'concerns': user_concerns,
        'site_title': 'My Concerns',
    }
    return render(request, 'communication/user_concerns.html', context)