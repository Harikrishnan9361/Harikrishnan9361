import uuid
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.db import connection
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.http import require_POST, require_http_methods

from .models import Category, Destination, Booking, UserProfile
from .forms import UserRegisterForm, BookingForm, ProfileEditForm, PaymentProcessForm


def health_check(request):
    """
    Production-safe health check endpoint.
    Verifies database connectivity without leaking internal connection details or credentials.
    """
    db_ok = False
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False

    status_code = 200 if db_ok else 503
    return JsonResponse({
        "status": "ok" if db_ok else "degraded",
        "service": "vahad-tms",
        "database": "connected" if db_ok else "unavailable",
    }, status=status_code)


def home(request):
    """Home landing page with top categories and featured destinations."""
    categories = Category.objects.all()[:10]
    featured_destinations = Destination.objects.filter(is_featured=True).select_related('category')[:8]
    return render(request, 'vahad_app/home.html', {
        'categories': categories,
        'featured_destinations': featured_destinations
    })


def register(request):
    """User registration view with input validation and profile creation."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now sign in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'vahad_app/register.html', {'form': form})


def about(request):
    """About VAHAD company & mission page."""
    return render(request, 'vahad_app/about.html')


def destinations(request):
    """Destination catalog with category filter, location filter, and multi-field keyword search."""
    category_id = request.GET.get('category')
    query = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()

    all_destinations = Destination.objects.all().select_related('category')

    # 1. Filter by Category
    if category_id:
        try:
            category_id = int(category_id)
            all_destinations = all_destinations.filter(category_id=category_id)
        except (ValueError, TypeError):
            category_id = None

    # 2. Filter by Location
    if location:
        all_destinations = all_destinations.filter(location__icontains=location)

    # 3. Filter by Search Query
    if query:
        keywords = query.split()
        search_filter = Q()
        for kw in keywords:
            search_filter |= (
                Q(name__icontains=kw) |
                Q(description__icontains=kw) |
                Q(location__icontains=kw) |
                Q(category__name__icontains=kw) |
                Q(best_time_to_visit__icontains=kw)
            )
        all_destinations = all_destinations.filter(search_filter).distinct()

    categories = Category.objects.all()

    return render(request, 'vahad_app/destinations.html', {
        'destinations': all_destinations,
        'categories': categories,
        'current_category': category_id,
        'search_query': query,
        'current_location': location
    })


def destination_detail(request, pk):
    """Destination details page with related recommendations."""
    destination = get_object_or_404(Destination.objects.select_related('category'), pk=pk)
    related_destinations = Destination.objects.filter(
        category=destination.category
    ).exclude(pk=destination.pk).select_related('category')[:3]

    if not related_destinations.exists():
        related_destinations = Destination.objects.exclude(pk=destination.pk).select_related('category')[:3]

    return render(request, 'vahad_app/destination_detail.html', {
        'destination': destination,
        'related_destinations': related_destinations,
    })


@login_required
def booking(request, destination_id):
    """
    Booking creation flow.
    Server-side validation with BookingForm and accurate Decimal price calculations.
    """
    destination = get_object_or_404(Destination, id=destination_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            customer_name = form.cleaned_data['customer_name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            address = form.cleaned_data.get('address', '')
            special_requests = form.cleaned_data.get('special_requests', '')
            travel_date = form.cleaned_data['travel_date']
            check_out_date = form.cleaned_data.get('check_out_date')
            num_travelers = form.cleaned_data['num_travelers']
            hotel_type = form.cleaned_data['hotel_type']
            transport = form.cleaned_data['transport']

            # Accurate Decimal Price Multipliers
            multiplier = Decimal("1.00")
            if hotel_type == 'Budget':
                multiplier = Decimal("0.80")
            elif hotel_type == 'Luxury':
                multiplier = Decimal("2.50")

            base_price = destination.price_estimate
            total_price = (base_price * Decimal(str(num_travelers)) * multiplier).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            booking_id = str(uuid.uuid4())[:8].upper()

            new_booking = Booking.objects.create(
                user=request.user,
                destination=destination,
                customer_name=customer_name,
                email=email,
                phone=phone,
                address=address,
                special_requests=special_requests,
                travel_date=travel_date,
                check_out_date=check_out_date,
                num_travelers=num_travelers,
                hotel_type=hotel_type,
                transport=transport,
                total_price=total_price,
                booking_id=booking_id,
                is_paid=False,
                booking_status="Pending",
                payment_method="Pending Payment"
            )
            return redirect('payment', booking_id=booking_id)
        else:
            # Add form validation errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        # Pre-populate defaults from logged-in user profile
        initial_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        initial_phone = getattr(request.user, 'userprofile', None).phone if hasattr(request.user, 'userprofile') else ''
        form = BookingForm(initial={
            'customer_name': initial_name,
            'email': request.user.email,
            'phone': initial_phone,
            'num_travelers': 1,
            'hotel_type': 'Standard',
            'transport': 'Flight'
        })

    return render(request, 'vahad_app/booking.html', {
        'destination': destination,
        'form': form
    })


@login_required
def payment(request, booking_id):
    """
    Secure Payment View.
    Enforces booking ownership.
    GET: Displays payment options and DEMO simulation details.
    POST: Processes payment authorization via CSRF-protected form submission.
    """
    booking_obj = get_object_or_404(Booking, booking_id=booking_id, user=request.user)

    if request.method == 'POST':
        form = PaymentProcessForm(request.POST)
        if form.is_valid():
            method = form.cleaned_data['payment_method']
            vip_opted = form.cleaned_data.get('vip_protection', False)

            # Apply VIP Protection add-on if selected and not previously applied
            if vip_opted and not booking_obj.is_paid:
                vip_cost = Decimal("2999.00")
                booking_obj.total_price = (booking_obj.total_price + vip_cost).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )

            booking_obj.payment_method = method
            booking_obj.is_paid = True
            booking_obj.booking_status = "Confirmed"
            booking_obj.save()

            messages.success(request, f"Payment simulation completed ({method}). Your booking is confirmed!")
            return redirect('confirmation', booking_id=booking_obj.booking_id)
        else:
            messages.error(request, "Invalid payment selection. Please choose a valid payment method.")

    return render(request, 'vahad_app/payment.html', {
        'booking': booking_obj
    })


@login_required
def confirmation(request, booking_id):
    """
    Booking Confirmation / Digital Ticket Receipt.
    Strictly read-only GET view with ownership verification.
    """
    booking_obj = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    return render(request, 'vahad_app/confirmation.html', {'booking': booking_obj})


@login_required
def profile(request):
    """User profile dashboard displaying personal details and user-isolated booking history."""
    UserProfile.objects.get_or_create(user=request.user)
    bookings = Booking.objects.filter(user=request.user).select_related('destination').order_by('-created_at')
    points = bookings.count() * 150

    return render(request, 'vahad_app/profile.html', {
        'bookings': bookings,
        'points': points
    })


def premium(request):
    """VAHAD Premium tier presentation page."""
    return render(request, 'vahad_app/premium.html')


@login_required
def rewards(request):
    """
    Gamified Loyalty Rewards Program.
    Server-side calculations for tier progression and available point balance.
    """
    UserProfile.objects.get_or_create(user=request.user)
    bookings_count = Booking.objects.filter(user=request.user).count()
    points = bookings_count * 150

    # Determine tier levels and percentage progress
    if points <= 1000:
        level = "Explorer"
        next_tier = "1,000"
        points_pct = min(100, int((points / 1000) * 100)) if points > 0 else 0
    elif points <= 3000:
        level = "Voyager"
        next_tier = "3,000"
        points_pct = min(100, int(((points - 1000) / 2000) * 100))
    elif points <= 5000:
        level = "Globe Trotter"
        next_tier = "5,000"
        points_pct = min(100, int(((points - 3000) / 2000) * 100))
    else:
        level = "Vahad Legend"
        next_tier = "Max Tier"
        points_pct = 100

    return render(request, 'vahad_app/rewards.html', {
        'points': points,
        'level': level,
        'bookings_count': bookings_count,
        'next_tier': next_tier,
        'points_pct': points_pct
    })


@login_required
@require_POST
def edit_profile(request):
    """Update profile information with image and email validation."""
    form = ProfileEditForm(request.POST, request.FILES, user=request.user)
    if form.is_valid():
        user = request.user
        user.first_name = form.cleaned_data.get('first_name', user.first_name)
        user.last_name = form.cleaned_data.get('last_name', user.last_name)
        user.email = form.cleaned_data.get('email', user.email)
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        phone = form.cleaned_data.get('phone')
        if phone is not None:
            profile.phone = phone

        if 'profile_photo' in request.FILES and form.cleaned_data.get('profile_photo'):
            profile.profile_photo = form.cleaned_data['profile_photo']

        profile.save()
        messages.success(request, "Profile updated successfully!")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field.replace('_', ' ').title()}: {error}")

    return redirect('profile')


@login_required
@require_http_methods(["GET", "POST"])
def cancel_booking(request, booking_id):
    """Cancel an active booking with ownership verification."""
    booking_obj = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    if booking_obj.booking_status != "Cancelled":
        booking_obj.booking_status = "Cancelled"
        booking_obj.save()
        messages.success(request, f"Booking #{booking_obj.booking_id} has been cancelled.")
    else:
        messages.info(request, f"Booking #{booking_obj.booking_id} is already cancelled.")
    return redirect('profile')


def custom_404(request, exception=None):
    """Custom 404 error page."""
    return render(request, '404.html', status=404)


def custom_500(request):
    """Custom 500 error page."""
    return render(request, '500.html', status=500)


def custom_403(request, exception=None):
    """Custom 403 error page."""
    return render(request, '403.html', status=403)
