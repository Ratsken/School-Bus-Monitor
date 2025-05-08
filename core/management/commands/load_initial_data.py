from django.core.management.base import BaseCommand
from core.models import Bus, Route, CustomUser, Student, Concern, Notification, BusLocation
from django.utils import timezone
import random
from datetime import timedelta
import json

class Command(BaseCommand):
    help = 'Load comprehensive test data for the system'
    
    def handle(self, *args, **kwargs):
        # UAE school locations (latitude, longitude)
        SCHOOL_LOCATIONS = {
            'main_campus': (25.2048, 55.2708),  # Downtown Dubai
            'branch_1': (25.0764, 55.1324),     # Al Barsha
            'branch_2': (25.2676, 55.2927)      # Dubai International Academic City
        }
        
        # Residential areas in Dubai with coordinates
        RESIDENTIAL_AREAS = [
            {'name': 'Arabian Ranches', 'coords': (25.0605, 55.1830)},
            {'name': 'The Springs', 'coords': (25.0657, 55.1718)},
            {'name': 'Jumeirah', 'coords': (25.2249, 55.2517)},
            {'name': 'Mirdif', 'coords': (25.2205, 55.4025)},
            {'name': 'Al Nahda', 'coords': (25.2866, 55.3593)},
            {'name': 'Al Warqa', 'coords': (25.2484, 55.4128)},
            {'name': 'Discovery Gardens', 'coords': (25.0647, 55.1522)},
            {'name': 'Motor City', 'coords': (25.0438, 55.2176)}
        ]
        
        # Create admin user
        admin = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@school.com',
            password='admin123',
            role='admin',
            phone_number='+971501234567'
        )
        
        # Create school administrator
        school_admin = CustomUser.objects.create_user(
            username='school_admin',
            email='admin@modernschool.ae',
            password='admin123',
            role='admin',
            phone_number='+971501234568',
            first_name='Fatima',
            last_name='Al Maktoum'
        )
        
        # Create drivers
        drivers = []
        arabic_names = [
            ('Mohammed', 'Ali'),
            ('Ahmed', 'Hassan'),
            ('Omar', 'Khalid'),
            ('Youssef', 'Ibrahim'),
            ('Khalid', 'Mohammed'),
            ('Abdullah', 'Saif'),
            ('Ali', 'Omar'),
            ('Ibrahim', 'Ahmed')
        ]
        
        for i, (first, last) in enumerate(arabic_names, start=1):
            driver = CustomUser.objects.create_user(
                username=f'driver{i}',
                email=f'driver{i}@school.com',
                password=f'driver{i}123',
                role='driver',
                phone_number=f'+97150{1234560+i}',
                first_name=first,
                last_name=last
            )
            drivers.append(driver)
        
        # Create parents
        parents = []
        for i in range(1, 21):
            parent = CustomUser.objects.create_user(
                username=f'parent{i}',
                email=f'parent{i}@school.com',
                password=f'parent{i}123',
                role='parent',
                phone_number=f'+97155{1234560+i}',
                first_name=f'Parent{i}_First',
                last_name=f'Parent{i}_Last'
            )
            parents.append(parent)
        
        # Create buses with realistic UAE bus numbers
        buses = []
        bus_numbers = [
            'DXB-1001', 'DXB-1002', 'DXB-1003', 'DXB-1004',
            'DXB-2001', 'DXB-2002', 'DXB-2003', 'DXB-2004'
        ]
        
        for i, bus_num in enumerate(bus_numbers):
            bus = Bus.objects.create(
                bus_number=bus_num,
                capacity=random.choice([45, 50, 55]),
                driver=drivers[i] if i < len(drivers) else None,
                status=random.choice(['active', 'active', 'active', 'in_maintenance', 'delayed'])
            )
            buses.append(bus)
        
        # Create routes with realistic UAE school routes
        routes = []
        route_names = [
            'Morning Route - Arabian Ranches to Main Campus',
            'Morning Route - Jumeirah to Main Campus',
            'Morning Route - Mirdif to Branch 1',
            'Afternoon Route - Main Campus to Al Warqa',
            'Afternoon Route - Branch 1 to Discovery Gardens',
            'Evening Route - Branch 2 to Motor City',
            'Weekend Route - All Areas Shuttle'
        ]
        
        for i, name in enumerate(route_names):
            route = Route.objects.create(
                name=name,
                bus=buses[i] if i < len(buses) else None,
                start_time=timezone.now().replace(hour=6, minute=30 if i < 3 else 14, second=0),
                end_time=timezone.now().replace(hour=7, minute=45 if i < 3 else 15, second=30)
            )
            routes.append(route)
        
        # Create students with realistic names
        students = []
        arabic_student_names = [
            ('Aisha', 'Mohammed'),
            ('Fatima', 'Ahmed'),
            ('Mariam', 'Omar'),
            ('Layla', 'Khalid'),
            ('Zayed', 'Ali'),
            ('Salem', 'Hassan'),
            ('Noor', 'Ibrahim'),
            ('Hessa', 'Abdullah')
        ]
        
        for i, (first, last) in enumerate(arabic_student_names, start=1):
            student = Student.objects.create(
                first_name=first,
                last_name=last,
                parent=parents[i % len(parents)],
                assigned_route=routes[i % len(routes)],
                student_id=f'STU-2023-{i:03d}'
            )
            students.append(student)
        
        # Create additional students for more data
        for i in range(9, 41):
            area = RESIDENTIAL_AREAS[i % len(RESIDENTIAL_AREAS)]
            student = Student.objects.create(
                first_name=f'Student{i}_First',
                last_name=f'Student{i}_Last',
                parent=parents[i % len(parents)],
                assigned_route=routes[i % len(routes)],
                student_id=f'STU-2023-{i:03d}'
            )
            students.append(student)
        
        # Create bus locations with realistic movement patterns
        for bus in buses:
            if bus.status != 'active':
                continue
                
            # Generate a route of points from residential area to school
            route_points = []
            residential_area = random.choice(RESIDENTIAL_AREAS)
            school = random.choice(list(SCHOOL_LOCATIONS.values()))
            
            # Generate intermediate points (simulating a route)
            for j in range(10):
                lat = residential_area['coords'][0] + (school[0] - residential_area['coords'][0]) * (j/10)
                lng = residential_area['coords'][1] + (school[1] - residential_area['coords'][1]) * (j/10)
                route_points.append((lat, lng))
            
            # Create location records for this bus
            for j, (lat, lng) in enumerate(route_points):
                timestamp = timezone.now() - timedelta(minutes=len(route_points)-j)
                BusLocation.objects.create(
                    bus=bus,
                    latitude=lat,
                    longitude=lng,
                    timestamp=timestamp,
                    speed=random.randint(30, 60)  # km/h
                )
        
        # Create concerns
        concern_subjects = [
            'Bus arrived late',
            'Driver was speeding',
            'My child missed the bus',
            'Bus was too crowded',
            'Air conditioning not working',
            'Bus route changed without notice',
            'Driver was rude',
            'Bus was dirty'
        ]
        
        for i in range(20):
            Concern.objects.create(
                raised_by=random.choice(parents),
                bus=random.choice(buses),
                subject=random.choice(concern_subjects),
                description=f"Detailed description of the issue #{i+1}. " +
                           f"The problem occurred on {timezone.now().strftime('%Y-%m-%d')}.",
                status=random.choice(['open', 'in_progress', 'closed']),
                resolved_by=admin if random.random() > 0.7 else None,
                resolved_at=timezone.now() - timedelta(days=random.randint(1, 30)) if random.random() > 0.7 else None
            )
        
        # Create notifications
        notification_types = [
            ('Bus Delay', 'delay', 'The bus will be 15 minutes late due to traffic.'),
            ('Route Change', 'info', 'The afternoon route has been modified.'),
            ('Maintenance', 'maintenance', 'Bus DXB-1003 is undergoing maintenance.'),
            ('Weather Alert', 'alert', 'School buses may be delayed due to fog.')
        ]
        
        for i in range(15):
            subject, n_type, message = random.choice(notification_types)
            notification = Notification.objects.create(
                bus=random.choice(buses) if random.random() > 0.5 else None,
                sender=admin,
                recipient_group=random.choice(['parent', 'driver', 'admin']),
                subject=f"{subject} - {timezone.now().strftime('%m/%d')}",
                message=message,
                notification_type=n_type,
                sent_via=random.choice(['email', 'sms', 'system']),
                status=random.choice(['sent', 'pending', 'failed'])
            )
            
            # Add some recipients
            if random.random() > 0.5:
                if notification.recipient_group == 'parent':
                    notification.recipients.set(random.sample(parents, min(5, len(parents))))
                elif notification.recipient_group == 'driver':
                    notification.recipients.set(random.sample(drivers, min(3, len(drivers))))
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully loaded test data:\n'
            f'- {CustomUser.objects.count()} users\n'
            f'- {Bus.objects.count()} buses\n'
            f'- {Route.objects.count()} routes\n'
            f'- {Student.objects.count()} students\n'
            f'- {BusLocation.objects.count()} location records\n'
            f'- {Concern.objects.count()} concerns\n'
            f'- {Notification.objects.count()} notifications\n'
        ))