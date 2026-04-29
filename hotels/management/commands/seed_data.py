"""
Management command to seed initial sample data.
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from hotels.models import Hotel, Room
from food_services.models import MenuItem
from bookings.models import Coupon
from django.utils import timezone
from datetime import date, timedelta
import decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed sample data: hotels, rooms, users, menu items, coupons'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding sample data...')

        # ── Create admin user ──────────────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin', email='admin@smarthotel.com',
                password='Admin@1234', role='admin'
            )
            admin.phone = '+91-9876543210'
            admin.save()
            self.stdout.write(self.style.SUCCESS('Created admin user: admin / Admin@1234'))
        else:
            self.stdout.write('Admin user already exists.')

        # ── Create customer users ─────────────────────────────────────────
        demo_customers = [
            {'username': 'rahul', 'email': 'rahul@example.com', 'phone': '9811223344'},
            {'username': 'priya', 'email': 'priya@example.com', 'phone': '9922334455'},
            {'username': 'amit', 'email': 'amit@example.com', 'phone': '9833445566'},
        ]
        for cu in demo_customers:
            if not User.objects.filter(username=cu['username']).exists():
                u = User.objects.create_user(
                    username=cu['username'], email=cu['email'],
                    password='Customer@123', role='customer', phone=cu['phone']
                )
                from users.models import Profile
                Profile.objects.get_or_create(user=u)
                self.stdout.write(f"Created customer: {cu['username']} / Customer@123")

        # ── Create Hotels ─────────────────────────────────────────────────
        hotels_data = [
            {
                'name': 'The Grand Mumbai Palace',
                'description': 'Luxury hotel in the heart of Mumbai with world-class amenities, fine dining, and a rooftop pool.',
                'address': '14, Marine Drive, Nariman Point',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'latitude': '18.9322',
                'longitude': '72.8345',
                'rating': decimal.Decimal('4.7'),
                'phone': '+91-22-66789000',
                'email': 'info@grandmumbaipalace.com',
                'amenities': 'Pool, Spa, Gym, Restaurant, Bar, WiFi, Parking, Room Service',
            },
            {
                'name': 'Rajasthan Heritage Haveli',
                'description': 'Experience royal Rajasthani culture in this heritage property with stunning architecture and cultural shows.',
                'address': 'Sardar Patel Marg, Civil Lines',
                'city': 'Jaipur',
                'state': 'Rajasthan',
                'latitude': '26.9124',
                'longitude': '75.7873',
                'rating': decimal.Decimal('4.5'),
                'phone': '+91-141-2345678',
                'email': 'stay@rajhaveli.com',
                'amenities': 'Heritage Architecture, Rooftop Dining, Cultural Shows, Desert Safaris, WiFi, Parking',
            },
            {
                'name': 'Delhi Business Suites',
                'description': 'Modern business hotel with conference facilities, express check-in, and proximity to major corporate hubs.',
                'address': 'Connaught Place, Block A',
                'city': 'Delhi',
                'state': 'Delhi',
                'latitude': '28.6315',
                'longitude': '77.2167',
                'rating': decimal.Decimal('4.2'),
                'phone': '+91-11-43567890',
                'email': 'book@delhibusiness.com',
                'amenities': 'Conference Rooms, WiFi, Restaurant, Gym, Laundry, 24/7 Reception',
            },
            {
                'name': 'Goa Beach Resort',
                'description': 'Beachside resort with private access to pristine sandy beach, water sports, and sunset cruises.',
                'address': 'Calangute Beach Road',
                'city': 'Goa',
                'state': 'Goa',
                'latitude': '15.5490',
                'longitude': '73.7517',
                'rating': decimal.Decimal('4.8'),
                'phone': '+91-832-2458900',
                'email': 'info@goabeachresort.com',
                'amenities': 'Private Beach, Water Sports, Pool, Spa, Beach Bar, Sunset Cruise, WiFi',
            },
            {
                'name': 'Bengaluru Tech Stay',
                'description': 'Contemporary hotel tailored for tech professionals with co-working spaces and superfast internet.',
                'address': 'Koramangala 5th Block',
                'city': 'Bengaluru',
                'state': 'Karnataka',
                'latitude': '12.9352',
                'longitude': '77.6245',
                'rating': decimal.Decimal('4.0'),
                'phone': '+91-80-45609000',
                'email': 'stay@bengtech.com',
                'amenities': 'Co-working Space, WiFi 1Gbps, Café, Meeting Rooms, Gym, Valet Parking',
            },
            {
                'name': 'Shimla Mountain Retreat',
                'description': 'Peaceful hill station getaway with stunning Himalayan views, trekking trails, and a cozy fireplace lounge.',
                'address': 'Ridge Road, Near Christchurch',
                'city': 'Shimla',
                'state': 'Himachal Pradesh',
                'latitude': '31.1048',
                'longitude': '77.1734',
                'rating': decimal.Decimal('4.3'),
                'phone': '+91-177-2800901',
                'email': 'retreat@shimla.in',
                'amenities': 'Mountain View, Fireplace, Trekking, Restaurant, WiFi, Bonfire',
            },
        ]

        created_hotels = []
        for hd in hotels_data:
            hotel, created = Hotel.objects.get_or_create(
                name=hd['name'],
                defaults={
                    'description': hd['description'],
                    'address': hd['address'],
                    'city': hd['city'],
                    'state': hd['state'],
                    'country': 'India',
                    'latitude': hd['latitude'],
                    'longitude': hd['longitude'],
                    'rating': hd['rating'],
                    'phone': hd['phone'],
                    'email': hd['email'],
                    'amenities': hd['amenities'],
                }
            )
            created_hotels.append(hotel)
            if created:
                self.stdout.write(f'Created hotel: {hotel.name}')

        # ── Create Rooms ──────────────────────────────────────────────────
        room_templates = [
            {'room_number': '101', 'room_type': 'single', 'price': 1500, 'capacity': 1, 'floor': 1, 'amenities': 'AC, TV, WiFi'},
            {'room_number': '102', 'room_type': 'single', 'price': 1800, 'capacity': 1, 'floor': 1, 'amenities': 'AC, TV, WiFi, Minibar'},
            {'room_number': '201', 'room_type': 'double', 'price': 2800, 'capacity': 2, 'floor': 2, 'amenities': 'AC, TV, WiFi, King Bed'},
            {'room_number': '202', 'room_type': 'double', 'price': 3200, 'capacity': 2, 'floor': 2, 'amenities': 'AC, TV, WiFi, Sea View'},
            {'room_number': '301', 'room_type': 'deluxe', 'price': 5500, 'capacity': 2, 'floor': 3, 'amenities': 'AC, Smart TV, Bathtub, Balcony, WiFi'},
            {'room_number': '401', 'room_type': 'suite', 'price': 9500, 'capacity': 4, 'floor': 4, 'amenities': 'Living Room, Jacuzzi, Kitchen, Butler Service'},
        ]

        for hotel in created_hotels:
            for rt in room_templates:
                if not Room.objects.filter(hotel=hotel, room_number=rt['room_number']).exists():
                    Room.objects.create(
                        hotel=hotel,
                        room_number=rt['room_number'],
                        room_type=rt['room_type'],
                        price_per_night=decimal.Decimal(rt['price']),
                        capacity=rt['capacity'],
                        floor=rt['floor'],
                        amenities=rt['amenities'],
                        is_available=True,
                    )
            self.stdout.write(f'Rooms added for: {hotel.name}')

        # ── Create Menu Items ─────────────────────────────────────────────
        menu_items = [
            # Breakfast
            {'name': 'Masala Dosa', 'category': 'breakfast', 'price': 120, 'is_veg': True, 'description': 'Crispy dosa with spiced potato filling and chutneys'},
            {'name': 'Aloo Paratha', 'category': 'breakfast', 'price': 90, 'is_veg': True, 'description': 'Stuffed whole wheat flatbread with curd and pickle'},
            {'name': 'English Breakfast', 'category': 'breakfast', 'price': 280, 'is_veg': False, 'description': 'Eggs, toast, beans, sausages and hash browns'},
            {'name': 'Fruit Bowl', 'category': 'breakfast', 'price': 180, 'is_veg': True, 'description': 'Fresh seasonal fruits with honey'},
            # Lunch
            {'name': 'Paneer Butter Masala', 'category': 'lunch', 'price': 280, 'is_veg': True, 'description': 'Creamy tomato gravy with soft paneer'},
            {'name': 'Chicken Biryani', 'category': 'lunch', 'price': 350, 'is_veg': False, 'description': 'Aromatic basmati rice with spiced chicken'},
            {'name': 'Dal Makhani', 'category': 'lunch', 'price': 220, 'is_veg': True, 'description': 'Slow-cooked black lentils in butter and cream'},
            # Dinner
            {'name': 'Grilled Fish', 'category': 'dinner', 'price': 480, 'is_veg': False, 'description': 'Fresh catch of the day with herb marinade'},
            {'name': 'Veg Thali', 'category': 'dinner', 'price': 320, 'is_veg': True, 'description': '5 curries, rice, bread, salad and dessert'},
            {'name': 'Mutton Rogan Josh', 'category': 'dinner', 'price': 520, 'is_veg': False, 'description': 'Rich Kashmiri lamb curry'},
            # Snacks
            {'name': 'Samosa (2 pcs)', 'category': 'snacks', 'price': 60, 'is_veg': True, 'description': 'Crispy fried pastry with spiced filling'},
            {'name': 'Club Sandwich', 'category': 'snacks', 'price': 220, 'is_veg': False, 'description': 'Triple-decker sandwich with chicken and veggies'},
            {'name': 'Fresh Lime Soda', 'category': 'snacks', 'price': 80, 'is_veg': True, 'description': 'Refreshing lime soda sweet or salty'},
            # Desserts
            {'name': 'Gulab Jamun', 'category': 'desserts', 'price': 90, 'is_veg': True, 'description': 'Soft milk solids dumplings in rose syrup'},
            {'name': 'Chocolate Brownie', 'category': 'desserts', 'price': 180, 'is_veg': True, 'description': 'Warm fudge brownie with vanilla ice cream'},
        ]
        for mi_data in menu_items:
            MenuItem.objects.get_or_create(
                name=mi_data['name'],
                category=mi_data['category'],
                defaults={
                    'price': decimal.Decimal(mi_data['price']),
                    'is_veg': mi_data['is_veg'],
                    'description': mi_data['description'],
                    'is_available': True,
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Menu items seeded: {len(menu_items)}'))

        # ── Create Coupons ────────────────────────────────────────────────
        coupons = [
            {'code': 'WELCOME10', 'discount_type': 'percent', 'discount_value': 10, 'max_uses': 100},
            {'code': 'FLAT500', 'discount_type': 'flat', 'discount_value': 500, 'max_uses': 50},
            {'code': 'SUMMER20', 'discount_type': 'percent', 'discount_value': 20, 'max_uses': 30},
        ]
        today = date.today()
        for cp in coupons:
            Coupon.objects.get_or_create(
                code=cp['code'],
                defaults={
                    'discount_type': cp['discount_type'],
                    'discount_value': decimal.Decimal(cp['discount_value']),
                    'max_uses': cp['max_uses'],
                    'valid_from': today,
                    'valid_until': today + timedelta(days=365),
                    'is_active': True,
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Coupons seeded: {len(coupons)}'))

        self.stdout.write(self.style.SUCCESS('\n✅ Sample data seeded successfully!'))
        self.stdout.write('\nTest Credentials:')
        self.stdout.write('  Admin: admin / Admin@1234')
        self.stdout.write('  Customer: rahul / Customer@123')
        self.stdout.write('  Customer: priya / Customer@123')
        self.stdout.write('\nDiscount Coupons: WELCOME10, FLAT500, SUMMER20')
