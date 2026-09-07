from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='vahad_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('about/', views.about, name='about'),
    path('destinations/', views.destinations, name='destinations'),
    path('destination/<int:pk>/', views.destination_detail, name='destination_detail'),
    path('booking/<int:destination_id>/', views.booking, name='booking'),
    path('payment/<str:booking_id>/', views.payment, name='payment'),
    path('confirmation/<str:booking_id>/', views.confirmation, name='confirmation'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('rewards/', views.rewards, name='rewards'),
    path('booking/cancel/<str:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('premium/', views.premium, name='premium'),
    path('health/', views.health_check, name='health_check'),
]
