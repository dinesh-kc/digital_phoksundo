# users/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
# from . import views # Not needed for now, but good to keep if you add custom user views later

app_name = 'users' # IMPORTANT: This defines the namespace 'users:'

urlpatterns = [
    # Login view provided by Django
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    # Logout view provided by Django
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'), # Redirect to home after logout
    # Add password reset/change paths here later if needed (e.g., path('password_change/', auth_views.PasswordChangeView.as_view(...), name='password_change'))
]