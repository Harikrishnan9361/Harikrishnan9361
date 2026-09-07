from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    phone = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    class Meta:
        db_table = 'user_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
    else:
        if hasattr(instance, 'userprofile'):
            instance.userprofile.save()
        else:
            UserProfile.objects.get_or_create(user=instance)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        db_table = 'category'
        ordering = ['name']

    def __str__(self):
        return self.name


class Destination(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='destinations')
    location = models.CharField(max_length=200)
    description = models.TextField()
    best_time_to_visit = models.CharField(max_length=200, blank=True)
    price_estimate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("1000.00"))
    image = models.ImageField(upload_to='destination_images/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        db_table = 'destination'
        ordering = ['-is_featured', 'name']

    def __str__(self):
        return f"{self.name} ({self.location})"


class Booking(models.Model):
    HOTEL_TYPES = [
        ('Budget', 'Budget'),
        ('Standard', 'Standard'),
        ('Luxury', 'Luxury'),
    ]
    TRANSPORT_TYPES = [
        ('Bus', 'Bus'),
        ('Train', 'Train'),
        ('Flight', 'Flight'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='bookings')
    
    # Guest & Contact Information
    customer_name = models.CharField(max_length=150, default='Guest')
    email = models.EmailField(default='guest@example.com')
    phone = models.CharField(max_length=25, default='')
    special_requests = models.TextField(blank=True, default='')
    address = models.CharField(max_length=255, blank=True, default='')
    
    # Travel Dates
    travel_date = models.DateField()
    check_out_date = models.DateField(null=True, blank=True)
    
    # Booking Preferences
    num_travelers = models.PositiveIntegerField(default=1)
    hotel_type = models.CharField(max_length=20, choices=HOTEL_TYPES, default='Standard')
    transport = models.CharField(max_length=20, choices=TRANSPORT_TYPES, default='Flight')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    booking_id = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Payment & Status
    payment_method = models.CharField(max_length=50, blank=True, default='Pending Payment')
    booking_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Pending")
    is_paid = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'booking'
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking #{self.booking_id} - {self.customer_name} ({self.destination.name})"
