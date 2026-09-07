"""
Django management command to seed initial sample data for VAHAD-TMS.
Safe and idempotent: Can be executed multiple times without creating duplicate records or insecure superusers.
"""

from decimal import Decimal
from django.core.management.base import BaseCommand
from vahad_app.models import Category, Destination


def run_seed(stdout=None):
    def log(msg):
        if stdout:
            stdout.write(msg)
        else:
            print(msg)

    log("Populating database with sample categories and destinations...")

    # 10 Standard Categories
    categories_data = [
        ("Beaches", "Golden sands and blue waters.", "category_images/beaches.jpg"),
        ("Hill Stations", "Cool climates and misty peaks.", "category_images/hill_stations.jpg"),
        ("Historical Places", "Step back into India's rich past.", "category_images/historical.jpg"),
        ("Temples", "Spiritual journeys and architecture.", "category_images/temples.jpg"),
        ("Waterfalls", "Nature's majestic cascades.", "category_images/waterfalls.png"),
        ("Wildlife", "Encounter exotic animals in the wild.", "category_images/wildlife.png"),
        ("Cities", "Vibrant culture and modern life.", "category_images/cities.jpg"),
        ("Adventure", "Thrills and excitement await.", "category_images/adventure.png"),
        ("Cultural Heritage", "Rich traditions and arts.", "category_images/culture.png"),
        ("Luxury Resorts", "Relax in ultimate comfort.", "category_images/luxury.png")
    ]

    category_objs = {}
    for name, desc, img_path in categories_data:
        cat, created = Category.objects.update_or_create(
            name=name,
            defaults={
                'description': desc,
                'image': img_path
            }
        )
        category_objs[name] = cat
        action = "Created" if created else "Updated"
        log(f"  [{action}] Category: {name}")

    # Featured Destinations (Tamil Nadu + Pan-India)
    destinations_data = [
        ("Yercaud", "Hill Stations", "Salem, Tamil Nadu", "The Jewel of the South, famous for its coffee plantations and the Yercaud Lake.", Decimal("2500.00"), True, 'destination_images/yerkard.jpg', 'October to March'),
        ("Bhavani", "Historical Places", "Erode, Tamil Nadu", "Known for the Sangameswarar Temple and the confluence of rivers.", Decimal("1500.00"), True, 'destination_images/bhavani.jpg', 'October to March'),
        ("Marina Beach", "Beaches", "Chennai, Tamil Nadu", "The longest natural urban beach in the country.", Decimal("500.00"), True, 'destination_images/marina_beach.jpg', 'November to February'),
        ("Ooty", "Hill Stations", "Nilgiris, Tamil Nadu", "The Queen of Hill Stations, known for the Nilgiri Mountain Railway.", Decimal("3500.00"), True, 'destination_images/ooty.jpg', 'October to June'),
        ("Madurai", "Temples", "Madurai, Tamil Nadu", "The Temple City, home to the magnificent Meenakshi Amman Temple.", Decimal("2000.00"), True, 'destination_images/madurai.jpg', 'October to March'),
        ("Coimbatore", "Cities", "Coimbatore, Tamil Nadu", "The Manchester of South India.", Decimal("1800.00"), False, 'destination_images/coimbator.jpg', 'September to March'),
        ("Bengaluru", "Cities", "Karnataka", "The Silicon Valley of India.", Decimal("3000.00"), False, 'destination_images/bangalote.jpg', 'October to March'),
        ("Hyderabad", "Cities", "Telangana", "The City of Pearls.", Decimal("2800.00"), False, 'destination_images/hydhrapath.jpg', 'October to March'),
        ("Hampi", "Historical Places", "Karnataka", "The UNESCO World Heritage site known for its ancient ruins.", Decimal("3000.00"), False, 'destination_images/hampi.jpg', 'October to March'),
        ("Munnar", "Hill Stations", "Idukki, Kerala", "Breathtaking green tea plantations and misty hills.", Decimal("4000.00"), True, 'destination_images/munnar.png', 'September to May'),
        ("Goa", "Beaches", "Goa", "Scenic sun-kissed beaches and vibrant nightlife.", Decimal("4500.00"), True, 'destination_images/goa.png', 'November to February'),
        ("Taj Mahal", "Historical Places", "Agra, Uttar Pradesh", "The ultimate symbol of love and a UNESCO World Heritage site.", Decimal("5000.00"), True, 'destination_images/taj_mahal.png', 'October to March'),
        ("Manali", "Hill Stations", "Himachal Pradesh", "Snow-capped peaks, skiing, and adventure trails.", Decimal("5500.00"), True, 'destination_images/manali.png', 'October to June'),
    ]

    for name, cat_name, loc, desc, price, featured, img_path, best_time in destinations_data:
        cat = category_objs.get(cat_name)
        if cat:
            dest, created = Destination.objects.update_or_create(
                name=name,
                defaults={
                    'category': cat,
                    'location': loc,
                    'description': desc,
                    'price_estimate': price,
                    'is_featured': featured,
                    'image': img_path,
                    'best_time_to_visit': best_time
                }
            )
            action = "Created" if created else "Updated"
            log(f"  [{action}] Destination: {name}")

    log("Seed complete! All categories and destinations are up to date.")


class Command(BaseCommand):
    help = 'Seeds initial sample categories and destinations into the database (Idempotent).'

    def handle(self, *args, **options):
        run_seed(stdout=self.stdout)
