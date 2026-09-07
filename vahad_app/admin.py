from django.contrib import admin
from .models import UserProfile, Category, Destination, Booking


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'get_email']
    search_fields = ['user__username', 'user__email', 'phone']
    raw_id_fields = ['user']

    @admin.display(description='Email')
    def get_email(self, obj):
        return obj.user.email


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_destinations_count']
    search_fields = ['name', 'description']
    ordering = ['name']

    @admin.display(description='Total Destinations')
    def get_destinations_count(self, obj):
        return obj.destinations.count()


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'location', 'price_estimate', 'best_time_to_visit', 'is_featured']
    list_filter = ['category', 'is_featured', 'location']
    search_fields = ['name', 'location', 'description']
    list_editable = ['is_featured', 'price_estimate']
    ordering = ['-is_featured', 'name']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'booking_id', 'customer_name', 'destination', 'travel_date', 
        'num_travelers', 'total_price', 'payment_method', 'booking_status', 'is_paid', 'created_at'
    ]
    list_filter = [
        'booking_status', 'is_paid', 'payment_method', 
        'hotel_type', 'transport', 'travel_date', 'created_at'
    ]
    search_fields = ['booking_id', 'customer_name', 'email', 'phone', 'destination__name', 'user__username']
    readonly_fields = ['booking_id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    date_hierarchy = 'travel_date'
