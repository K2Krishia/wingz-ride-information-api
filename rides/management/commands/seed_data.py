from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from rides.models import User, Ride, RideEvent


class Command(BaseCommand):
    help = 'Seeds the database with test data for rides, users, and events'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))
        
        # clear existing data (optional - comment out to keep existing data)
        self.stdout.write('Clearing existing data...')
        RideEvent.objects.all().delete()
        Ride.objects.all().delete()
        User.objects.all().delete()
        
        # create admin users
        self.stdout.write('Creating admin users...')
        admin1 = User.objects.create_user(
            username='admin',
            email='admin@wingz.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='admin',
            phone_number='+1234567890',
            is_staff=True,
            is_superuser=True
        )
        
        admin2 = User.objects.create_user(
            username='admin2',
            email='admin2@wingz.com',
            password='admin123',
            first_name='Sarah',
            last_name='Admin',
            role='admin',
            phone_number='+1234567891'
        )
        
        # create drivers
        self.stdout.write('Creating drivers...')
        drivers = []
        driver_data = [
            ('john_driver', 'John', 'Smith', 'john.driver@wingz.com', '+1234567892'),
            ('jane_driver', 'Jane', 'Doe', 'jane.driver@wingz.com', '+1234567893'),
            ('mike_driver', 'Mike', 'Johnson', 'mike.driver@wingz.com', '+1234567894'),
            ('lisa_driver', 'Lisa', 'Brown', 'lisa.driver@wingz.com', '+1234567895'),
        ]
        
        for username, first_name, last_name, email, phone in driver_data:
            driver = User.objects.create_user(
                username=username,
                email=email,
                password='driver123',
                first_name=first_name,
                last_name=last_name,
                role='driver',
                phone_number=phone
            )
            drivers.append(driver)
        
        # create riders
        self.stdout.write('Creating riders...')
        riders = []
        rider_data = [
            ('alice_rider', 'Alice', 'Williams', 'alice@example.com', '+1234567896'),
            ('bob_rider', 'Bob', 'Davis', 'bob@example.com', '+1234567897'),
            ('carol_rider', 'Carol', 'Miller', 'carol@example.com', '+1234567898'),
            ('david_rider', 'David', 'Wilson', 'david@example.com', '+1234567899'),
            ('emma_rider', 'Emma', 'Taylor', 'emma@example.com', '+1234567800'),
            ('frank_rider', 'Frank', 'Anderson', 'frank@example.com', '+1234567801'),
        ]
        
        for username, first_name, last_name, email, phone in rider_data:
            rider = User.objects.create_user(
                username=username,
                email=email,
                password='rider123',
                first_name=first_name,
                last_name=last_name,
                role='rider',
                phone_number=phone
            )
            riders.append(rider)
        
        # create rides with various statuses and locations (San Francisco area)
        self.stdout.write('Creating rides...')
        now = timezone.now()
        
        rides_data = [
            # recent rides
            {
                'rider': riders[0],
                'driver': drivers[0],
                'status': 'completed',
                'pickup_lat': 37.7749,
                'pickup_lon': -122.4194,
                'dropoff_lat': 37.8044,
                'dropoff_lon': -122.2712,
                'pickup_time': now - timedelta(hours=2),
            },
            {
                'rider': riders[1],
                'driver': drivers[1],
                'status': 'in-progress',
                'pickup_lat': 37.7849,
                'pickup_lon': -122.4094,
                'dropoff_lat': 37.3382,
                'dropoff_lon': -121.8863,
                'pickup_time': now - timedelta(minutes=30),
            },
            {
                'rider': riders[2],
                'driver': drivers[2],
                'status': 'pickup',
                'pickup_lat': 37.7649,
                'pickup_lon': -122.4294,
                'dropoff_lat': 37.4419,
                'dropoff_lon': -122.1430,
                'pickup_time': now - timedelta(minutes=10),
            },
            {
                'rider': riders[3],
                'driver': drivers[3],
                'status': 'en-route',
                'pickup_lat': 37.7949,
                'pickup_lon': -122.3994,
                'dropoff_lat': 37.6879,
                'dropoff_lon': -122.4702,
                'pickup_time': now + timedelta(minutes=15),
            },
            {
                'rider': riders[4],
                'driver': None,
                'status': 'requested',
                'pickup_lat': 37.8049,
                'pickup_lon': -122.4394,
                'dropoff_lat': 37.5485,
                'dropoff_lon': -121.9886,
                'pickup_time': now + timedelta(hours=1),
            },
            # older rides
            {
                'rider': riders[0],
                'driver': drivers[1],
                'status': 'completed',
                'pickup_lat': 37.7549,
                'pickup_lon': -122.4494,
                'dropoff_lat': 37.8716,
                'dropoff_lon': -122.2727,
                'pickup_time': now - timedelta(days=1),
            },
            {
                'rider': riders[1],
                'driver': drivers[0],
                'status': 'completed',
                'pickup_lat': 37.7349,
                'pickup_lon': -122.4594,
                'dropoff_lat': 37.9577,
                'dropoff_lon': -122.3477,
                'pickup_time': now - timedelta(days=2),
            },
            {
                'rider': riders[2],
                'driver': drivers[2],
                'status': 'cancelled',
                'pickup_lat': 37.7149,
                'pickup_lon': -122.4694,
                'dropoff_lat': 37.7749,
                'dropoff_lon': -122.4194,
                'pickup_time': now - timedelta(days=3),
            },
            # future scheduled rides
            {
                'rider': riders[5],
                'driver': None,
                'status': 'requested',
                'pickup_lat': 37.7249,
                'pickup_lon': -122.4794,
                'dropoff_lat': 37.6213,
                'dropoff_lon': -122.3790,
                'pickup_time': now + timedelta(days=1),
            },
            {
                'rider': riders[3],
                'driver': drivers[3],
                'status': 'en-route',
                'pickup_lat': 37.7449,
                'pickup_lon': -122.4894,
                'dropoff_lat': 37.8715,
                'dropoff_lon': -122.2730,
                'pickup_time': now + timedelta(hours=3),
            },
        ]
        
        rides = []
        for ride_data in rides_data:
            ride = Ride.objects.create(
                id_rider=ride_data['rider'],
                id_driver=ride_data['driver'],
                status=ride_data['status'],
                pickup_latitude=ride_data['pickup_lat'],
                pickup_longitude=ride_data['pickup_lon'],
                dropoff_latitude=ride_data['dropoff_lat'],
                dropoff_longitude=ride_data['dropoff_lon'],
                pickup_time=ride_data['pickup_time']
            )
            rides.append(ride)
        
        # create ride events
        self.stdout.write('Creating ride events...')
        
        # events for ride 1 (completed) - mix of old and recent
        RideEvent.objects.create(
            id_ride=rides[0],
            description='Ride requested',
            created_at=now - timedelta(hours=2, minutes=30)
        )
        RideEvent.objects.create(
            id_ride=rides[0],
            description='Driver assigned',
            created_at=now - timedelta(hours=2, minutes=25)
        )
        RideEvent.objects.create(
            id_ride=rides[0],
            description='Driver en route to pickup',
            created_at=now - timedelta(hours=2, minutes=20)
        )
        RideEvent.objects.create(
            id_ride=rides[0],
            description='Driver arrived at pickup location',
            created_at=now - timedelta(hours=2, minutes=10)
        )
        RideEvent.objects.create(
            id_ride=rides[0],
            description='Passenger picked up',
            created_at=now - timedelta(hours=2, minutes=5)
        )
        RideEvent.objects.create(
            id_ride=rides[0],
            description='Ride completed',
            created_at=now - timedelta(hours=1, minutes=40)
        )
        
        # events for ride 2 (in-progress) - all recent (within 24 hours)
        RideEvent.objects.create(
            id_ride=rides[1],
            description='Ride requested',
            created_at=now - timedelta(minutes=45)
        )
        RideEvent.objects.create(
            id_ride=rides[1],
            description='Driver assigned',
            created_at=now - timedelta(minutes=40)
        )
        RideEvent.objects.create(
            id_ride=rides[1],
            description='Driver en route',
            created_at=now - timedelta(minutes=35)
        )
        RideEvent.objects.create(
            id_ride=rides[1],
            description='Passenger picked up',
            created_at=now - timedelta(minutes=30)
        )
        
        # events for ride 3 (pickup)
        RideEvent.objects.create(
            id_ride=rides[2],
            description='Ride requested',
            created_at=now - timedelta(minutes=15)
        )
        RideEvent.objects.create(
            id_ride=rides[2],
            description='Driver assigned',
            created_at=now - timedelta(minutes=12)
        )
        RideEvent.objects.create(
            id_ride=rides[2],
            description='Driver arrived',
            created_at=now - timedelta(minutes=10)
        )
        
        # events for ride 4 (en-route)
        RideEvent.objects.create(
            id_ride=rides[3],
            description='Ride requested',
            created_at=now - timedelta(minutes=5)
        )
        RideEvent.objects.create(
            id_ride=rides[3],
            description='Driver assigned',
            created_at=now - timedelta(minutes=3)
        )
        
        # events for older rides (> 24 hours ago, to test the filtering)
        RideEvent.objects.create(
            id_ride=rides[5],
            description='Ride completed',
            created_at=now - timedelta(days=1, hours=1)
        )
        RideEvent.objects.create(
            id_ride=rides[6],
            description='Ride completed',
            created_at=now - timedelta(days=2, hours=1)
        )
        RideEvent.objects.create(
            id_ride=rides[7],
            description='Ride cancelled by passenger',
            created_at=now - timedelta(days=3, hours=1)
        )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded database!'))
        self.stdout.write(self.style.SUCCESS(f'Created:'))
        self.stdout.write(f'  - {User.objects.filter(role="admin").count()} admin users')
        self.stdout.write(f'  - {User.objects.filter(role="driver").count()} drivers')
        self.stdout.write(f'  - {User.objects.filter(role="rider").count()} riders')
        self.stdout.write(f'  - {Ride.objects.count()} rides')
        self.stdout.write(f'  - {RideEvent.objects.count()} ride events')
        self.stdout.write(self.style.SUCCESS('\\nTest credentials:'))
        self.stdout.write('  Admin: admin@wingz.com / admin123')
        self.stdout.write('  Driver: john.driver@wingz.com / driver123')
        self.stdout.write('  Rider: alice@example.com / rider123')
