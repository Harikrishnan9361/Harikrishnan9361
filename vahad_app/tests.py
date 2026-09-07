import uuid
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Category, Destination, Booking, UserProfile


class VahadModelTests(TestCase):
    """Unit tests for data models and signals."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='traveler1',
            email='traveler1@example.com',
            password='Password@123',
            first_name='Alex',
            last_name='Morgan'
        )
        self.category = Category.objects.create(
            name='Hill Stations',
            description='Cool mountains and misty valleys'
        )
        self.destination = Destination.objects.create(
            name='Ooty',
            category=self.category,
            location='Nilgiris, Tamil Nadu',
            description='Queen of Hill Stations',
            best_time_to_visit='October to June',
            price_estimate=Decimal('3500.00'),
            is_featured=True
        )

    def test_user_profile_signal(self):
        """Test that UserProfile is automatically created on User creation."""
        self.assertTrue(hasattr(self.user, 'userprofile'))
        self.assertEqual(str(self.user.userprofile), "traveler1's Profile")

    def test_category_creation(self):
        """Test Category string representation and ordering."""
        self.assertEqual(str(self.category), 'Hill Stations')

    def test_destination_creation(self):
        """Test Destination string representation and attributes."""
        self.assertEqual(str(self.destination), 'Ooty (Nilgiris, Tamil Nadu)')
        self.assertEqual(self.destination.category.name, 'Hill Stations')
        self.assertEqual(self.destination.price_estimate, Decimal('3500.00'))

    def test_booking_creation(self):
        """Test Booking model creation and string representation."""
        booking = Booking.objects.create(
            user=self.user,
            destination=self.destination,
            customer_name='Alex Morgan',
            email='alex@example.com',
            phone='+919876543210',
            travel_date=date.today() + timedelta(days=7),
            num_travelers=2,
            hotel_type='Standard',
            transport='Flight',
            total_price=Decimal('7000.00'),
            booking_id='BKTEST01',
            is_paid=False,
            booking_status='Pending'
        )
        self.assertIn('BKTEST01', str(booking))
        self.assertIn('Alex Morgan', str(booking))
        self.assertIn('Ooty', str(booking))


class VahadViewAndFlowTests(TestCase):
    """Comprehensive test suite covering all views, authentication, authorization, and workflows."""

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user_alice',
            email='alice@example.com',
            password='AlicePassword@123',
            first_name='Alice',
            last_name='Walker'
        )
        self.user2 = User.objects.create_user(
            username='user_bob',
            email='bob@example.com',
            password='BobPassword@123',
            first_name='Bob',
            last_name='Ross'
        )
        self.category_beaches = Category.objects.create(
            name='Beaches',
            description='Sunny coasts and blue tides'
        )
        self.category_hills = Category.objects.create(
            name='Hill Stations',
            description='Cool misty heights'
        )
        self.destination_goa = Destination.objects.create(
            name='Goa',
            category=self.category_beaches,
            location='Goa, India',
            description='Vibrant coastal getaway with sun-kissed beaches.',
            best_time_to_visit='November to February',
            price_estimate=Decimal('4500.00'),
            is_featured=True
        )
        self.destination_munnar = Destination.objects.create(
            name='Munnar',
            category=self.category_hills,
            location='Idukki, Kerala',
            description='Lush tea gardens and misty peaks.',
            best_time_to_visit='September to May',
            price_estimate=Decimal('4000.00'),
            is_featured=False
        )

    # 1. Home Page
    def test_home_view(self):
        """Test home page loads with categories and featured destinations."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vahad_app/home.html')
        self.assertIn('categories', response.context)
        self.assertIn('featured_destinations', response.context)
        self.assertEqual(len(response.context['featured_destinations']), 1)

    # 2. About & Premium Pages
    def test_about_and_premium_views(self):
        """Test static content pages."""
        r_about = self.client.get(reverse('about'))
        self.assertEqual(r_about.status_code, 200)
        self.assertTemplateUsed(r_about, 'vahad_app/about.html')

        r_prem = self.client.get(reverse('premium'))
        self.assertEqual(r_prem.status_code, 200)
        self.assertTemplateUsed(r_prem, 'vahad_app/premium.html')

    # 3. Registration View (Valid and Duplicate Handling)
    def test_registration_valid_and_duplicate(self):
        """Test user registration form validation."""
        r_get = self.client.get(reverse('register'))
        self.assertEqual(r_get.status_code, 200)

        # Valid registration
        post_data = {
            'username': 'new_traveler',
            'full_name': 'New Traveler',
            'email': 'new_traveler@example.com',
            'phone': '+919988776655',
            'password1': 'StrongPass@2026',
            'password2': 'StrongPass@2026',
        }
        r_post = self.client.post(reverse('register'), post_data)
        self.assertEqual(r_post.status_code, 302)
        self.assertTrue(User.objects.filter(username='new_traveler').exists())

        # Duplicate email registration attempt
        r_dup = self.client.post(reverse('register'), post_data)
        self.assertEqual(r_dup.status_code, 200)
        self.assertFormError(r_dup.context['form'], 'username', 'A user with that username already exists.')

    # 4. Login and Logout
    def test_login_logout(self):
        """Test authentication login and logout redirects."""
        login_success = self.client.login(username='user_alice', password='AlicePassword@123')
        self.assertTrue(login_success)

        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

        # Logout
        self.client.logout()
        r_after_logout = self.client.get(reverse('profile'))
        self.assertEqual(r_after_logout.status_code, 302)

    # 5. Destination Catalog & Filters
    def test_destinations_catalog_and_filtering(self):
        """Test destination list, search, category, and location filters."""
        # Catalog all
        r_all = self.client.get(reverse('destinations'))
        self.assertEqual(r_all.status_code, 200)
        self.assertEqual(len(r_all.context['destinations']), 2)

        # Filter category
        r_cat = self.client.get(reverse('destinations'), {'category': self.category_beaches.id})
        self.assertEqual(r_cat.status_code, 200)
        self.assertEqual(len(r_cat.context['destinations']), 1)
        self.assertEqual(r_cat.context['destinations'][0].name, 'Goa')

        # Filter location
        r_loc = self.client.get(reverse('destinations'), {'location': 'Kerala'})
        self.assertEqual(r_loc.status_code, 200)
        self.assertEqual(len(r_loc.context['destinations']), 1)
        self.assertEqual(r_loc.context['destinations'][0].name, 'Munnar')

        # Search keyword
        r_search = self.client.get(reverse('destinations'), {'q': 'coastal'})
        self.assertEqual(r_search.status_code, 200)
        self.assertEqual(len(r_search.context['destinations']), 1)

    # 6. Destination Detail View
    def test_destination_detail(self):
        """Test destination details and recommendations."""
        response = self.client.get(reverse('destination_detail', args=[self.destination_goa.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['destination'].name, 'Goa')
        self.assertIn('related_destinations', response.context)

    # 7. Booking Authentication Guard
    def test_booking_requires_login(self):
        """Unauthenticated user accessing booking page must be redirected to login."""
        response = self.client.get(reverse('booking', args=[self.destination_goa.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    # 8. Booking Form Validation & Past Date Rejection
    def test_booking_validation_and_past_date(self):
        """Test booking form validation rejects past dates and invalid travelers."""
        self.client.login(username='user_alice', password='AlicePassword@123')

        # Past travel date
        past_date = (date.today() - timedelta(days=5)).strftime('%Y-%m-%d')
        invalid_data = {
            'customer_name': 'Alice Walker',
            'email': 'alice@example.com',
            'phone': '+919876543210',
            'travel_date': past_date,
            'num_travelers': 2,
            'hotel_type': 'Standard',
            'transport': 'Flight',
        }
        response = self.client.post(reverse('booking', args=[self.destination_goa.id]), invalid_data)
        self.assertEqual(response.status_code, 200)
        # Booking should not have been created
        self.assertEqual(Booking.objects.filter(user=self.user1).count(), 0)

    # 9. Booking Creation with Accurate Decimal Pricing
    def test_booking_creation_decimal_multipliers(self):
        """Test booking creation with Decimal pricing calculations for Standard, Budget, and Luxury."""
        self.client.login(username='user_alice', password='AlicePassword@123')

        future_date = (date.today() + timedelta(days=15)).strftime('%Y-%m-%d')
        post_data = {
            'customer_name': 'Alice Walker',
            'email': 'alice@example.com',
            'phone': '+919876543210',
            'travel_date': future_date,
            'num_travelers': 3,
            'hotel_type': 'Luxury',  # Multiplier 2.5
            'transport': 'Flight',
            'special_requests': 'Ocean view suite'
        }
        response = self.client.post(reverse('booking', args=[self.destination_goa.id]), post_data)
        self.assertEqual(response.status_code, 302)

        booking = Booking.objects.get(user=self.user1)
        # Goa base: 4500.00 * 3 travelers * 2.5 luxury = 33750.00
        expected_total = Decimal('4500.00') * Decimal('3') * Decimal('2.50')
        self.assertEqual(booking.total_price, expected_total)
        self.assertFalse(booking.is_paid)
        self.assertEqual(booking.booking_status, 'Pending')

    # 10. IDOR Authorization Protection (Cross-User Security)
    def test_booking_payment_and_confirmation_idor_protection(self):
        """Ensure users CANNOT view or confirm another user's booking by manipulating booking_id."""
        # Create booking belonging to User 1 (Alice)
        alice_booking = Booking.objects.create(
            user=self.user1,
            destination=self.destination_goa,
            customer_name='Alice Walker',
            email='alice@example.com',
            phone='+919876543210',
            travel_date=date.today() + timedelta(days=20),
            num_travelers=1,
            hotel_type='Standard',
            transport='Flight',
            total_price=Decimal('4500.00'),
            booking_id='ALICEBK01'
        )

        # Log in as User 2 (Bob)
        self.client.login(username='user_bob', password='BobPassword@123')

        # Bob attempts to view Alice's payment page -> Must return 404
        r_pay = self.client.get(reverse('payment', args=[alice_booking.booking_id]))
        self.assertEqual(r_pay.status_code, 404)

        # Bob attempts to POST payment to Alice's booking -> Must return 404
        r_pay_post = self.client.post(reverse('payment', args=[alice_booking.booking_id]), {
            'payment_method': 'Credit / Debit Card'
        })
        self.assertEqual(r_pay_post.status_code, 404)

        # Bob attempts to view Alice's confirmation page -> Must return 404
        r_conf = self.client.get(reverse('confirmation', args=[alice_booking.booking_id]))
        self.assertEqual(r_conf.status_code, 404)

        # Bob attempts to cancel Alice's booking -> Must return 404
        r_cancel = self.client.get(reverse('cancel_booking', args=[alice_booking.booking_id]))
        self.assertEqual(r_cancel.status_code, 404)

        # Verify Alice's booking is unchanged
        alice_booking.refresh_from_db()
        self.assertFalse(alice_booking.is_paid)
        self.assertEqual(alice_booking.booking_status, 'Pending')

    # 11. Secure Payment POST Simulation Workflow
    def test_secure_payment_post_flow(self):
        """Test authorized user submitting payment POST with VIP Protection add-on."""
        self.client.login(username='user_alice', password='AlicePassword@123')

        booking = Booking.objects.create(
            user=self.user1,
            destination=self.destination_goa,
            customer_name='Alice Walker',
            email='alice@example.com',
            phone='+919876543210',
            travel_date=date.today() + timedelta(days=10),
            num_travelers=1,
            hotel_type='Standard',
            transport='Flight',
            total_price=Decimal('4500.00'),
            booking_id='ALICEPAY01',
            is_paid=False,
            booking_status='Pending'
        )

        # GET payment page
        r_get_pay = self.client.get(reverse('payment', args=[booking.booking_id]))
        self.assertEqual(r_get_pay.status_code, 200)
        self.assertTemplateUsed(r_get_pay, 'vahad_app/payment.html')

        # POST payment with VIP add-on (+2999.00)
        pay_post_data = {
            'payment_method': 'UPI / QR Payment',
            'vip_protection': 'true'
        }
        r_post_pay = self.client.post(reverse('payment', args=[booking.booking_id]), pay_post_data)
        self.assertEqual(r_post_pay.status_code, 302)
        self.assertRedirects(r_post_pay, reverse('confirmation', args=[booking.booking_id]))

        booking.refresh_from_db()
        self.assertTrue(booking.is_paid)
        self.assertEqual(booking.booking_status, 'Confirmed')
        self.assertEqual(booking.payment_method, 'UPI / QR Payment')
        self.assertEqual(booking.total_price, Decimal('7499.00'))  # 4500 + 2999

        # Confirmation Page View
        r_conf = self.client.get(reverse('confirmation', args=[booking.booking_id]))
        self.assertEqual(r_conf.status_code, 200)
        self.assertTemplateUsed(r_conf, 'vahad_app/confirmation.html')

    # 12. Profile and Rewards Isolation
    def test_profile_and_rewards_view(self):
        """Test profile shows only the logged-in user's bookings and correct reward points."""
        # Alice has 1 confirmed booking
        Booking.objects.create(
            user=self.user1,
            destination=self.destination_goa,
            customer_name='Alice Walker',
            email='alice@example.com',
            phone='+919876543210',
            travel_date=date.today() + timedelta(days=12),
            num_travelers=1,
            hotel_type='Standard',
            transport='Flight',
            total_price=Decimal('4500.00'),
            booking_id='ALICEBKRW',
            is_paid=True,
            booking_status='Confirmed'
        )
        # Bob has 0 bookings
        self.client.login(username='user_bob', password='BobPassword@123')
        r_prof_bob = self.client.get(reverse('profile'))
        self.assertEqual(r_prof_bob.status_code, 200)
        self.assertEqual(r_prof_bob.context['bookings'].count(), 0)
        self.assertEqual(r_prof_bob.context['points'], 0)

        # Login as Alice
        self.client.login(username='user_alice', password='AlicePassword@123')
        r_prof_alice = self.client.get(reverse('profile'))
        self.assertEqual(r_prof_alice.status_code, 200)
        self.assertEqual(r_prof_alice.context['bookings'].count(), 1)
        self.assertEqual(r_prof_alice.context['points'], 150)

        # Rewards page
        r_rewards = self.client.get(reverse('rewards'))
        self.assertEqual(r_rewards.status_code, 200)
        self.assertEqual(r_rewards.context['points'], 150)
        self.assertEqual(r_rewards.context['level'], 'Explorer')

    # 13. Profile Edit View
    def test_profile_edit(self):
        """Test profile information update."""
        self.client.login(username='user_alice', password='AlicePassword@123')
        post_data = {
            'first_name': 'Alicia',
            'last_name': 'Keyes',
            'email': 'alicia@example.com',
            'phone': '+919123456789'
        }
        response = self.client.post(reverse('edit_profile'), post_data)
        self.assertEqual(response.status_code, 302)

        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, 'Alicia')
        self.assertEqual(self.user1.email, 'alicia@example.com')
        self.assertEqual(self.user1.userprofile.phone, '+919123456789')

    # 14. Booking Cancellation by Owner
    def test_booking_cancellation_by_owner(self):
        """Test user can cancel their own active booking."""
        self.client.login(username='user_alice', password='AlicePassword@123')
        booking = Booking.objects.create(
            user=self.user1,
            destination=self.destination_munnar,
            customer_name='Alice Walker',
            email='alice@example.com',
            phone='+919876543210',
            travel_date=date.today() + timedelta(days=5),
            num_travelers=1,
            hotel_type='Standard',
            transport='Bus',
            total_price=Decimal('4000.00'),
            booking_id='ALICECANCEL01',
            is_paid=False,
            booking_status='Pending'
        )

        response = self.client.get(reverse('cancel_booking', args=[booking.booking_id]))
        self.assertEqual(response.status_code, 302)

        booking.refresh_from_db()
        self.assertEqual(booking.booking_status, 'Cancelled')

    # 15. Health Check Endpoint
    def test_health_check_endpoint(self):
        """Test health check returns HTTP 200 and operational JSON status."""
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'ok')
        self.assertEqual(data.get('service'), 'vahad-tms')
        self.assertEqual(data.get('database'), 'connected')

    # 16. Custom 404 / 403 / 500 error views
    def test_custom_error_pages(self):
        """Test custom error pages rendering without errors."""
        r_404 = self.client.get('/non-existent-random-page-url/')
        self.assertEqual(r_404.status_code, 404)
        self.assertTemplateUsed(r_404, '404.html')
