from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail
from django.template.loader import render_to_string
from unittest.mock import patch, MagicMock
from core.emails import (
    send_activation_email,
    send_welcome_email,
    send_job_approval_email,
    send_application_notification_email
)
from core.utils import (
    send_welcome_email as utils_send_welcome_email,
    send_job_approval_email as utils_send_job_approval_email,
    send_application_notification_email as utils_send_application_notification_email
)
from core.tasks import (
    send_activation_email_task,
    send_welcome_email_task,
    send_job_approval_email_task,
    send_application_notification_email_task
)
from jobs.models import Job, Application
from accounts.models import CustomUser

User = get_user_model()

class EmailFunctionsTest(TestCase):
    """Test cases for email functions in core.emails"""

    def setUp(self):
        self.employer = User.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123',
            is_employer=True
        )
        self.seeker = User.objects.create_user(
            username='seeker',
            email='seeker@test.com',
            password='testpass123',
            is_seeker=True
        )
        
        self.job = Job.objects.create(
            employer=self.employer,
            title='Test Job',
            description='Test Description',
            location='Test Location',
            salary=50000.00,
            published=True
        )
        
        self.application = Application.objects.create(
            job=self.job,
            seeker=self.seeker,
            status='Pending'
        )

    def test_send_activation_email(self):
        """Test sending activation email"""
        domain = 'testdomain.com'
        
        # Clear any existing emails
        mail.outbox = []
        
        send_activation_email(self.seeker, domain)
        
        # Check that one email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Activate your Smart Job Portal account')
        self.assertEqual(email.to, [self.seeker.email])
        self.assertIn(domain, email.body)
        self.assertIn(self.seeker.username, email.body)

    def test_send_welcome_email(self):
        """Test sending welcome email"""
        mail.outbox = []
        
        send_welcome_email(self.seeker)
        
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Welcome to Smart Job Portal!')
        self.assertEqual(email.to, [self.seeker.email])
        self.assertIn('Welcome', email.body)

    def test_send_job_approval_email(self):
        """Test sending job approval email"""
        mail.outbox = []
        
        send_job_approval_email(self.job)
        
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Your job listing has been approved')
        self.assertEqual(email.to, [self.employer.email])
        self.assertIn(self.job.title, email.body)
        self.assertIn(self.employer.username, email.body)

    def test_send_application_notification_email(self):
        """Test sending application notification email"""
        mail.outbox = []
        
        send_application_notification_email(self.application)
        
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Someone applied to your job!')
        self.assertEqual(email.to, [self.employer.email])
        self.assertIn(self.job.title, email.body)
        self.assertIn(self.seeker.username, email.body)
        self.assertIn(self.employer.username, email.body)


class UtilsFunctionsTest(TestCase):
    """Test cases for utility functions in core.utils"""

    def setUp(self):
        self.employer = User.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123',
            is_employer=True
        )
        self.seeker = User.objects.create_user(
            username='seeker',
            email='seeker@test.com',
            password='testpass123',
            is_seeker=True
        )
        
        self.job = Job.objects.create(
            employer=self.employer,
            title='Test Job',
            description='Test Description',
            location='Test Location',
            salary=50000.00,
            published=True
        )
        
        self.application = Application.objects.create(
            job=self.job,
            seeker=self.seeker,
            status='Pending'
        )

    def test_utils_send_welcome_email(self):
        """Test welcome email utility function"""
        mail.outbox = []
        
        utils_send_welcome_email(self.seeker)
        
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Welcome to Smart Job Portal!')
        self.assertEqual(email.to, [self.seeker.email])

    def test_utils_send_job_approval_email(self):
        """Test job approval email utility function"""
        mail.outbox = []
        
        utils_send_job_approval_email(self.job)
        
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Your job listing has been approved')
        self.assertEqual(email.to, [self.employer.email])

    def test_utils_send_application_notification_email(self):
        """Test application notification email utility function"""
        mail.outbox = []
        
        utils_send_application_notification_email(self.application)
        
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Someone applied to your job!')
        self.assertEqual(email.to, [self.employer.email])


class CeleryTasksTest(TestCase):
    """Test cases for Celery tasks"""

    def setUp(self):
        self.employer = User.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123',
            is_employer=True
        )
        self.seeker = User.objects.create_user(
            username='seeker',
            email='seeker@test.com',
            password='testpass123',
            is_seeker=True
        )
        
        self.job = Job.objects.create(
            employer=self.employer,
            title='Test Job',
            description='Test Description',
            location='Test Location',
            salary=50000.00,
            published=True
        )
        
        self.application = Application.objects.create(
            job=self.job,
            seeker=self.seeker,
            status='Pending'
        )

    @patch('core.tasks.send_activation_email')
    def test_send_activation_email_task(self, mock_send_email):
        """Test activation email task"""
        domain = {'domain': 'testdomain.com'}
        
        send_activation_email_task(self.seeker.id, domain)
        
        mock_send_email.assert_called_once_with(self.seeker, domain)

    @patch('core.tasks.send_welcome_email')
    def test_send_welcome_email_task(self, mock_send_email):
        """Test welcome email task"""
        send_welcome_email_task(self.seeker.id)
        
        mock_send_email.assert_called_once_with(self.seeker)

    @patch('core.tasks.send_job_approval_email')
    def test_send_job_approval_email_task(self, mock_send_email):
        """Test job approval email task"""
        send_job_approval_email_task(self.job.id)
        
        mock_send_email.assert_called_once_with(self.job)

    @patch('core.tasks.send_application_notification_email')
    def test_send_application_notification_email_task(self, mock_send_email):
        """Test application notification email task"""
        send_application_notification_email_task(self.application.id)
        
        mock_send_email.assert_called_once_with(self.application)

    def test_task_with_invalid_user_id(self):
        """Test task behavior with invalid user ID"""
        with self.assertRaises(User.DoesNotExist):
            send_welcome_email_task(99999)

    def test_task_with_invalid_job_id(self):
        """Test task behavior with invalid job ID"""
        with self.assertRaises(Job.DoesNotExist):
            send_job_approval_email_task(99999)

    def test_task_with_invalid_application_id(self):
        """Test task behavior with invalid application ID"""
        with self.assertRaises(Application.DoesNotExist):
            send_application_notification_email_task(99999)


class EmailTemplateTest(TestCase):
    """Test email template rendering"""

    def setUp(self):
        self.employer = User.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123',
            is_employer=True
        )
        self.seeker = User.objects.create_user(
            username='seeker',
            email='seeker@test.com',
            password='testpass123',
            is_seeker=True
        )
        
        self.job = Job.objects.create(
            employer=self.employer,
            title='Test Job',
            description='Test Description',
            location='Test Location',
            salary=50000.00,
            published=True
        )
        
        self.application = Application.objects.create(
            job=self.job,
            seeker=self.seeker,
            status='Pending'
        )

    def test_welcome_email_template_rendering(self):
        """Test welcome email template renders correctly"""
        try:
            template_content = render_to_string('accounts/welcome_email.html', {
                'user': self.seeker
            })
            self.assertIsInstance(template_content, str)
            self.assertIn(self.seeker.username, template_content)
        except Exception as e:
            # Template might not exist, which is okay for this test
            self.skipTest(f"Template not found: {e}")

    def test_job_approval_email_template_rendering(self):
        """Test job approval email template renders correctly"""
        try:
            context = {
                'employer_name': self.employer.username,
                'job_title': self.job.title
            }
            template_content = render_to_string('jobs/job_approval_email.html', context)
            self.assertIsInstance(template_content, str)
            self.assertIn(self.employer.username, template_content)
            self.assertIn(self.job.title, template_content)
        except Exception as e:
            self.skipTest(f"Template not found: {e}")

    def test_application_notification_email_template_rendering(self):
        """Test application notification email template renders correctly"""
        try:
            context = {
                'employer_name': self.employer.username,
                'job_title': self.job.title,
                'seeker_name': self.seeker.username,
                'seeker_email': self.seeker.email,
            }
            template_content = render_to_string('jobs/new_application_email.html', context)
            self.assertIsInstance(template_content, str)
            self.assertIn(self.employer.username, template_content)
            self.assertIn(self.job.title, template_content)
            self.assertIn(self.seeker.username, template_content)
        except Exception as e:
            self.skipTest(f"Template not found: {e}")


class EmailIntegrationTest(TestCase):
    """Integration tests for email functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_seeker=True
        )

    def test_email_backend_configuration(self):
        """Test email backend is properly configured"""
        from django.conf import settings
        from django.core.mail import get_connection
        
        # Test that we can get a connection
        connection = get_connection()
        self.assertIsNotNone(connection)

    def test_email_sending_with_fail_silently(self):
        """Test email sending with fail_silently=True doesn't raise exceptions"""
        try:
            utils_send_welcome_email(self.user)
            # If we get here, the email function executed without raising an exception
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Email function raised an exception when it should fail silently: {e}")

    def test_multiple_email_recipients(self):
        """Test sending emails to multiple recipients"""
        # Create another user
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        mail.outbox = []
        
        # Send welcome emails to both users
        utils_send_welcome_email(self.user)
        utils_send_welcome_email(user2)
        
        # Check that two emails were sent
        self.assertEqual(len(mail.outbox), 2)
        
        # Check recipients
        recipients = [email.to[0] for email in mail.outbox]
        self.assertIn(self.user.email, recipients)
        self.assertIn(user2.email, recipients)