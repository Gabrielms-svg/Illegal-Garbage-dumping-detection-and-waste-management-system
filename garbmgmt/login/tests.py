from django.test import TestCase, SimpleTestCase, Client
from django.urls import reverse, resolve
from .models import Normal_user, Authority_user, LegalDumpingLocation, Camera, DumpingEvent, NumberPlate, GarbageReport, GarbageEvidence
from django.utils import timezone
from . import views
from django.contrib.auth.hashers import make_password

class TestModels(TestCase):
    def setUp(self):
        self.normal_user = Normal_user.objects.create(
            fullname="Test User",
            username="testuser",
            email="test@example.com",
            phone="1234567890",
            password=make_password("password123")
        )
        
        self.auth_user = Authority_user.objects.create(
            first_name="Auth",
            last_name="User",
            auth_id="AUTH001",
            email="auth@example.com",
            phone="0987654321",
            password="password123"
        )
        
        self.camera = Camera.objects.create(
            camera_id="CAM01",
            location="Test Street"
        )

    def test_normal_user_creation(self):
        self.assertEqual(self.normal_user.fullname, "Test User")
        self.assertEqual(self.normal_user.email, "test@example.com")
        self.assertEqual(self.normal_user.phone, "1234567890")

    def test_authority_user_creation(self):
        self.assertEqual(self.auth_user.auth_id, "AUTH001")
        self.assertEqual(self.auth_user.email, "auth@example.com")
        self.assertEqual(self.auth_user.first_name, "Auth")

    def test_camera_str(self):
        self.assertEqual(str(self.camera), "CAM01 (Test Street)")

class TestUrls(SimpleTestCase):
    def test_home_url_resolves(self):
        url = reverse('home')
        self.assertEqual(resolve(url).func, views.home)

    def test_about_url_resolves(self):
        url = reverse('about')
        self.assertEqual(resolve(url).func, views.about)

    def test_user_login_url_resolves(self):
        url = reverse('user_login')
        self.assertEqual(resolve(url).func, views.user_login)

    def test_auth_login_url_resolves(self):
        url = reverse('auth_login')
        self.assertEqual(resolve(url).func, views.auth_login)

    def test_user_dashboard_url_resolves(self):
        url = reverse('user_dashboard')
        self.assertEqual(resolve(url).func, views.user_dashboard)

class TestViews(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_view_GET(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_about_view_GET(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about.html')

    def test_user_login_view_GET(self):
        response = self.client.get(reverse('user_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_login.html')

    def test_auth_login_view_GET(self):
        response = self.client.get(reverse('auth_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth_login.html')

    def test_user_dashboard_unauthenticated(self):
        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 302) # Redirects to user_login

    def test_auth_dashboard_unauthenticated(self):
        response = self.client.get(reverse('auth_dashboard'))
        self.assertEqual(response.status_code, 302) # Redirects to auth_login
