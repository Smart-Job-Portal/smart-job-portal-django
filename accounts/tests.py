from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from accounts.forms import CustomUserCreationForm
from accounts.tokens import account_activation_token
from accounts.models import CustomUser
from unittest.mock import patch

User = get_user_model()

class CustomUserModelTest(TestCase):
    """Test cases for CustomUser model"""
    
    def setUp(self):
        self.employer = User.objects.create_user(
            username='testemployer',
            email='employer@test.com',
            password='testpass123',
            is_employer=True
        )
        self.seeker = User.objects.create_user(
            username='testseeker',
            email='seeker@test.com',
            password='testpass123',
            is_seeker=True
        )

    def test_user_creation(self):
        """Test user creation with custom fields"""
        self.assertTrue(self.employer.is_employer)
        self.assertFalse(self.employer.is_seeker)
        self.assertTrue(self.seeker.is_seeker)
        self.assertFalse(self.seeker.is_employer)

    def test_user_str_representation(self):
        """Test string representation of user"""
        self.assertEqual(str(self.employer), 'testemployer')
        self.assertEqual(str(self.seeker), 'testseeker')

    def test_user_defaults(self):
        """Test default values for user fields"""
        user = User.objects.create_user(
            username='defaultuser',
            email='default@test.com',
            password='testpass123'
        )
        self.assertFalse(user.is_employer)
        self.assertFalse(user.is_seeker)


class CustomUserCreationFormTest(TestCase):
    """Test cases for CustomUserCreationForm"""

    def test_valid_form_employer(self):
        """Test form with valid employer data"""
        form_data = {
            'username': 'newemployer',
            'email': 'new@employer.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'role': 'employer'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_valid_form_seeker(self):
        """Test form with valid seeker data"""
        form_data = {
            'username': 'newseeker',
            'email': 'new@seeker.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'role': 'seeker'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        """Test form with invalid email"""
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'role': 'employer'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_password_mismatch(self):
        """Test form with password mismatch"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'complexpass123',
            'password2': 'differentpass123',
            'role': 'employer'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_save_employer(self):
        """Test form save creates employer user"""
        form_data = {
            'username': 'testemployer',
            'email': 'test@employer.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'role': 'employer'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertTrue(user.is_employer)
        self.assertFalse(user.is_seeker)

    def test_form_save_seeker(self):
        """Test form save creates seeker user"""
        form_data = {
            'username': 'testseeker',
            'email': 'test@seeker.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'role': 'seeker'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertTrue(user.is_seeker)
        self.assertFalse(user.is_employer)


class AccountViewsTest(TestCase):
    """Test cases for account views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_seeker=True
        )

    def test_register_view_get(self):
        """Test register view GET request"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register as')
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)

    @patch('accounts.views.send_activation_email_task.delay')
    def test_register_view_post_valid(self, mock_email_task):
        """Test register view POST with valid data"""
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'role': 'seeker'
        }
        response = self.client.post(reverse('register'), data=form_data)
        
        # Check user was created but not active
        user = User.objects.get(username='newuser')
        self.assertFalse(user.is_active)
        self.assertTrue(user.is_seeker)
        
        # Check email task was called
        mock_email_task.assert_called_once()
        
        # Check redirect to success page
        self.assertContains(response, 'please_check_email')

    def test_register_view_post_invalid(self):
        """Test register view POST with invalid data"""
        form_data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'complexpass123',
            'password2': 'differentpass',
            'role': 'seeker'
        }
        response = self.client.post(reverse('register'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', 'Enter a valid email address.')

    def test_activate_account_valid_token(self):
        """Test account activation with valid token"""
        # Create inactive user
        user = User.objects.create_user(
            username='inactiveuser',
            email='inactive@example.com',
            password='testpass123',
            is_active=False,
            is_seeker=True
        )
        
        # Generate activation token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        
        with patch('accounts.views.send_welcome_email_task.delay') as mock_welcome_task, \
             patch('accounts.views.send_welcome_email') as mock_welcome_sync:
            
            response = self.client.get(
                reverse('activate', kwargs={'uidb64': uid, 'token': token})
            )
            
            # Check user is now active and logged in
            user.refresh_from_db()
            self.assertTrue(user.is_active)
            
            # Check welcome emails were sent
            mock_welcome_task.assert_called_once_with(user.id)
            mock_welcome_sync.assert_called_once_with(user)
            
            # Check redirect to dashboard
            self.assertRedirects(response, reverse('dashboard'))

    def test_activate_account_invalid_token(self):
        """Test account activation with invalid token"""
        user = User.objects.create_user(
            username='inactiveuser',
            email='inactive@example.com',
            password='testpass123',
            is_active=False
        )
        
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        invalid_token = 'invalid-token'
        
        response = self.client.get(
            reverse('activate', kwargs={'uidb64': uid, 'token': invalid_token})
        )
        
        # Check user is still inactive
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        
        # Check error message
        self.assertContains(response, 'Activation link is invalid!')

    def test_login_view(self):
        """Test login view"""
        self.user.is_active = True
        self.user.save()
        
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        
        # Test login
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, '/dashboard/')

    def test_logout_view(self):
        """Test logout view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))


class EmailTokenTest(TestCase):
    """Test cases for email verification tokens"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_token_generation_and_verification(self):
        """Test token generation and verification"""
        token = account_activation_token.make_token(self.user)
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)
        
        # Test valid token
        self.assertTrue(account_activation_token.check_token(self.user, token))
        
        # Test invalid token
        self.assertFalse(account_activation_token.check_token(self.user, 'invalid-token'))


class AccountURLsTest(TestCase):
    """Test URL patterns for accounts app"""

    def test_register_url_resolves(self):
        """Test register URL resolves correctly"""
        url = reverse('register')
        self.assertEqual(url, '/accounts/register/')

    def test_login_url_resolves(self):
        """Test login URL resolves correctly"""
        url = reverse('login')
        self.assertEqual(url, '/accounts/login/')

    def test_logout_url_resolves(self):
        """Test logout URL resolves correctly"""
        url = reverse('logout')
        self.assertEqual(url, '/accounts/logout/')

    def test_activate_url_resolves(self):
        """Test activate URL resolves correctly"""
        url = reverse('activate', kwargs={'uidb64': 'test', 'token': 'test'})
        self.assertEqual(url, '/accounts/activate/test/test/')

    def test_password_reset_urls_resolve(self):
        """Test password reset URLs resolve correctly"""
        urls = [
            ('password_reset', '/accounts/password_reset/'),
            ('password_reset_done', '/accounts/password_reset/done/'),
            ('password_reset_complete', '/accounts/reset/done/'),
        ]
        
        for name, expected_url in urls:
            with self.subTest(url_name=name):
                url = reverse(name)
                self.assertEqual(url, expected_url)


class AdminIntegrationTest(TestCase):
    """Test admin integration for CustomUser"""

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
        self.client.login(username='admin', password='adminpass123')

    def test_custom_user_admin_registration(self):
        """Test CustomUser is registered in admin"""
        response = self.client.get('/admin/accounts/customuser/')
        self.assertEqual(response.status_code, 200)

    def test_custom_user_admin_add(self):
        """Test adding user through admin"""
        response = self.client.get('/admin/accounts/customuser/add/')
        self.assertEqual(response.status_code, 200)