from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db import IntegrityError
from unittest.mock import patch, MagicMock
from jobs.models import Job, Application, ActiveJobManager
from jobs.forms import ApplicationForm
from jobs.views import (
    JobListView, JobDetailView, JobCreateView, JobUpdateView, JobDeleteView,
    apply_job, job_applications, accept_application, reject_application
)
from core.utils import send_application_notification_email, send_job_approval_email

User = get_user_model()

class JobModelTest(TestCase):
    """Test cases for Job model"""

    def setUp(self):
        self.employer = User.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123',
            is_employer=True
        )

    def test_job_creation(self):
        """Test job creation with all required fields"""
        job = Job.objects.create(
            employer=self.employer,
            title='Test Job',
            description='Test Description',
            location='Test Location',
            salary=50000.00
        )
        
        self.assertEqual(job.employer, self.employer)
        self.assertEqual(job.title, 'Test Job')
        self.assertEqual(job.description, 'Test Description')
        self.assertEqual(job.location, 'Test Location')
        self.assertEqual(job.salary, 50000.00)
        self.assertFalse(job.published)  # Default should be False
        self.assertIsNotNone(job.posted_on)

    def test_job_str_representation(self):
        """Test job string representation"""
        job = Job.objects.create(
            employer=self.employer,
            title='Test Job',
            description='Test Description',
            location='Test Location',
            salary=50000.00
        )
        self.assertEqual(str(job), 'Test Job')

    def test_job_published_default_false(self):
        """Test job published field defaults to False"""
        job = Job.objects.create(
            employer=self.employer,
            title='Test Job',
            description='Test Description',
            location='Test Location',
            salary=50000.00
        )
        self.assertFalse(job.published)

    def test_active_job_manager(self):
        """Test ActiveJobManager only returns published jobs"""
        # Create published job
        published_job = Job.objects.create(
            employer=self.employer,
            title='Published Job',
            description='Description',
            location='Location',
            salary=50000.00,
            published=True
        )
        
        # Create unpublished job
        unpublished_job = Job.objects.create(
            employer=self.employer,
            title='Unpublished Job',
            description='Description',
            location='Location',
            salary=60000.00,
            published=False
        )
        
        # Test active jobs manager
        active_jobs = Job.active_jobs.active()
        self.assertIn(published_job, active_jobs)
        self.assertNotIn(unpublished_job, active_jobs)
        self.assertEqual(active_jobs.count(), 1)

    def test_job_foreign_key_relationship(self):
        """Test job-employer relationship"""
        job = Job.objects.create(
            employer=self.employer,
            title='Test Job',
            description='Description',
            location='Location',
            salary=50000.00
        )
        
        # Test reverse relationship
        self.assertIn(job, self.employer.jobs.all())


class ApplicationModelTest(TestCase):
    """Test cases for Application model"""

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
            description='Description',
            location='Location',
            salary=50000.00,
            published=True
        )

    def test_application_creation(self):
        """Test application creation"""
        application = Application.objects.create(
            job=self.job,
            seeker=self.seeker
        )
        
        self.assertEqual(application.job, self.job)
        self.assertEqual(application.seeker, self.seeker)
        self.assertEqual(application.status, 'Pending')  # Default status
        self.assertIsNotNone(application.applied_on)

    def test_application_str_representation(self):
        """Test application string representation"""
        application = Application.objects.create(
            job=self.job,
            seeker=self.seeker
        )
        expected_str = f"{self.seeker.username} applied for {self.job.title}"
        self.assertEqual(str(application), expected_str)

    def test_application_status_choices(self):
        """Test application status choices"""
        application = Application.objects.create(
            job=self.job,
            seeker=self.seeker
        )
        
        # Test valid statuses
        valid_statuses = ['Pending', 'Accepted', 'Rejected']
        for status in valid_statuses:
            application.status = status
            application.save()
            application.refresh_from_db()
            self.assertEqual(application.status, status)

    def test_application_resume_field(self):
        """Test application resume field"""
        resume_content = b'fake resume content'
        resume_file = SimpleUploadedFile(
            'resume.pdf',
            resume_content,
            content_type='application/pdf'
        )
        
        application = Application.objects.create(
            job=self.job,
            seeker=self.seeker,
            resume=resume_file
        )
        
        self.assertIsNotNone(application.resume)
        self.assertTrue(application.resume.name.startswith('resumes/'))

    @patch('core.utils.send_application_notification_email')
    def test_application_signal_sends_email(self, mock_send_email):
        """Test signal sends email when application is created"""
        Application.objects.create(
            job=self.job,
            seeker=self.seeker
        )
        
        mock_send_email.assert_called_once()


class ApplicationFormTest(TestCase):
    """Test cases for ApplicationForm"""

    def test_valid_form_with_pdf(self):
        """Test form with valid PDF file"""
        resume_content = b'%PDF-1.4 fake pdf content'
        resume_file = SimpleUploadedFile(
            'resume.pdf',
            resume_content,
            content_type='application/pdf'
        )
        
        form = ApplicationForm(files={'resume': resume_file})
        self.assertTrue(form.is_valid())

    def test_valid_form_with_doc(self):
        """Test form with valid DOC file"""
        resume_content = b'fake doc content'
        resume_file = SimpleUploadedFile(
            'resume.doc',
            resume_content,
            content_type='application/msword'
        )
        
        form = ApplicationForm(files={'resume': resume_file})
        self.assertTrue(form.is_valid())

    def test_valid_form_with_docx(self):
        """Test form with valid DOCX file"""
        resume_content = b'fake docx content'
        resume_file = SimpleUploadedFile(
            'resume.docx',
            resume_content,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
        form = ApplicationForm(files={'resume': resume_file})
        self.assertTrue(form.is_valid())

    def test_invalid_form_with_large_file(self):
        """Test form with file larger than 5MB"""
        # Create a file larger than 5MB
        large_content = b'x' * (6 * 1024 * 1024)  # 6MB
        large_file = SimpleUploadedFile(
            'large_resume.pdf',
            large_content,
            content_type='application/pdf'
        )
        
        form = ApplicationForm(files={'resume': large_file})
        self.assertFalse(form.is_valid())
        self.assertIn('resume', form.errors)
        self.assertIn('exceeds 5MB', str(form.errors['resume']))

    def test_invalid_form_with_wrong_format(self):
        """Test form with invalid file format"""
        invalid_file = SimpleUploadedFile(
            'resume.txt',
            b'text content',
            content_type='text/plain'
        )
        
        form = ApplicationForm(files={'resume': invalid_file})
        self.assertFalse(form.is_valid())
        self.assertIn('resume', form.errors)
        self.assertIn('Invalid file format', str(form.errors['resume']))

    def test_form_without_file(self):
        """Test form without resume file"""
        form = ApplicationForm()
        # Form should still be valid as resume is not required in the model
        # but the widget has required='required', so this depends on implementation


class JobViewsTest(TestCase):
    """Test cases for job views"""

    def setUp(self):
        self.client = Client()
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

    def test_job_list_view(self):
        """Test job list view displays published jobs"""
        response = self.client.get(reverse('job_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Job')

    def test_job_list_view_filters_unpublished(self):
        """Test job list view filters out unpublished jobs"""
        unpublished_job = Job.objects.create(
            employer=self.employer,
            title='Unpublished Job',
            description='Description',
            location='Location',
            salary=60000.00,
            published=False
        )
        
        response = self.client.get(reverse('job_list'))
        self.assertContains(response, 'Test Job')
        self.assertNotContains(response, 'Unpublished Job')

    def test_job_list_view_search(self):
        """Test job list view search functionality"""
        response = self.client.get(reverse('job_list'), {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Job')

    def test_job_list_view_location_filter(self):
        """Test job list view location filter"""
        response = self.client.get(reverse('job_list'), {'location': 'Test Location'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Job')

    def test_job_list_view_salary_filter(self):
        """Test job list view salary filter"""
        response = self.client.get(reverse('job_list'), {'salary': '50000'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Job')

    def test_job_detail_view(self):
        """Test job detail view"""
        response = self.client.get(reverse('job_detail', kwargs={'pk': self.job.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.job.title)
        self.assertContains(response, self.job.description)

    def test_job_detail_view_employer_context(self):
        """Test job detail view shows employer flag when user is job owner"""
        self.client.login(username='employer', password='testpass123')
        response = self.client.get(reverse('job_detail', kwargs={'pk': self.job.pk}))
        
        self.assertTrue(response.context['is_employer'])

    def test_job_detail_view_non_employer_context(self):
        """Test job detail view doesn't show employer flag for non-owners"""
        self.client.login(username='seeker', password='testpass123')
        response = self.client.get(reverse('job_detail', kwargs={'pk': self.job.pk}))
        
        self.assertFalse(response.context['is_employer'])

    def test_job_create_view_requires_login(self):
        """Test job create view requires authentication"""
        response = self.client.get(reverse('job_create'))
        self.assertRedirects(response, '/accounts/login/?next=/jobs/create/')

    def test_job_create_view_authenticated(self):
        """Test job create view when authenticated"""
        self.client.login(username='employer', password='testpass123')
        response = self.client.get(reverse('job_create'))
        self.assertEqual(response.status_code, 200)

    def test_job_create_post(self):
        """Test creating job via POST"""
        self.client.login(username='employer', password='testpass123')
        
        job_data = {
            'title': 'New Job',
            'description': 'New Description',
            'location': 'New Location',
            'salary': '70000.00'
        }
        
        response = self.client.post(reverse('job_create'), data=job_data)
        self.assertRedirects(response, reverse('job_list'))
        
        # Check job was created
        new_job = Job.objects.get(title='New Job')
        self.assertEqual(new_job.employer, self.employer)

    def test_job_update_view_requires_owner(self):
        """Test job update view requires job owner"""
        other_employer = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='testpass123',
            is_employer=True
        )
        
        self.client.login(username='other', password='testpass123')
        response = self.client.get(reverse('job_update', kwargs={'pk': self.job.pk}))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_job_update_view_owner(self):
        """Test job update view for job owner"""
        self.client.login(username='employer', password='testpass123')
        response = self.client.get(reverse('job_update', kwargs={'pk': self.job.pk}))
        self.assertEqual(response.status_code, 200)

    def test_job_delete_view_requires_owner(self):
        """Test job delete view requires job owner"""
        other_employer = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='testpass123',
            is_employer=True
        )
        
        self.client.login(username='other', password='testpass123')
        response = self.client.get(reverse('job_delete', kwargs={'pk': self.job.pk}))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_job_delete_view_owner(self):
        """Test job delete view for job owner"""
        self.client.login(username='employer', password='testpass123')
        response = self.client.get(reverse('job_delete', kwargs={'pk': self.job.pk}))
        self.assertEqual(response.status_code, 200)

    def test_apply_job_requires_login(self):
        """Test apply job view requires authentication"""
        response = self.client.get(reverse('apply_job', kwargs={'job_id': self.job.pk}))
        self.assertRedirects(response, f'/accounts/login/?next=/jobs/{self.job.pk}/apply/')

    def test_apply_job_requires_seeker(self):
        """Test apply job view requires seeker role"""
        self.client.login(username='employer', password='testpass123')
        response = self.client.get(reverse('apply_job', kwargs={'job_id': self.job.pk}))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_apply_job_get(self):
        """Test apply job GET request"""
        self.client.login(username='seeker', password='testpass123')
        response = self.client.get(reverse('apply_job', kwargs={'job_id': self.job.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], ApplicationForm)

    @patch('core.utils.send_application_notification_email')
    def test_apply_job_post(self, mock_send_email):
        """Test apply job POST request"""
        self.client.login(username='seeker', password='testpass123')
        
        resume_file = SimpleUploadedFile(
            'resume.pdf',
            b'fake resume content',
            content_type='application/pdf'
        )
        
        response = self.client.post(
            reverse('apply_job', kwargs={'job_id': self.job.pk}),
            {'resume': resume_file}
        )
        
        self.assertRedirects(response, reverse('job_list'))
        
        # Check application was created
        application = Application.objects.get(job=self.job, seeker=self.seeker)
        self.assertEqual(application.status, 'Pending')
