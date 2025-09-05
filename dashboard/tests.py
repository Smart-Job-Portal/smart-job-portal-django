from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from jobs.models import Job, Application
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class DashboardViewTest(TestCase):
    """Test cases for dashboard views"""

    def setUp(self):
        self.client = Client()
        
        # Create test users
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
        
        self.unknown_user = User.objects.create_user(
            username='unknown',
            email='unknown@test.com',
            password='testpass123'
        )
        
        # Create test jobs
        self.job1 = Job.objects.create(
            employer=self.employer,
            title='Test Job 1',
            description='Test Description 1',
            location='Test Location 1',
            salary=50000.00,
            published=True
        )
        
        self.job2 = Job.objects.create(
            employer=self.employer,
            title='Test Job 2',
            description='Test Description 2',
            location='Test Location 2',
            salary=60000.00,
            published=False  # Unpublished job
        )
        
        # Create test applications
        self.application1 = Application.objects.create(
            job=self.job1,
            seeker=self.seeker,
            status='Pending'
        )
        
        self.application2 = Application.objects.create(
            job=self.job1,
            seeker=self.seeker,
            status='Accepted'
        )

    def test_dashboard_redirect_when_not_logged_in(self):
        """Test dashboard redirects to login when user is not authenticated"""
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/')

    def test_employer_dashboard_view(self):
        """Test employer dashboard displays correct data"""
        self.client.login(username='employer', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/employer_dashboard.html')
        
        # Check context data
        self.assertIn('jobs', response.context)
        self.assertIn('applications', response.context)
        
        # Check jobs (only active/published ones)
        jobs = response.context['jobs']
        self.assertEqual(jobs.count(), 1)  # Only published job
        self.assertEqual(jobs.first().title, 'Test Job 1')
        
        # Check applications
        applications = response.context['applications']
        self.assertEqual(applications.count(), 2)  # Both applications to employer's job

    def test_seeker_dashboard_view(self):
        """Test seeker dashboard displays correct data"""
        self.client.login(username='seeker', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/seeker_dashboard.html')
        
        # Check context data
        self.assertIn('applications', response.context)
        
        # Check applications (seeker's applications)
        applications = response.context['applications']
        self.assertEqual(applications.count(), 2)  # Both applications by this seeker

    def test_unknown_role_dashboard_view(self):
        """Test dashboard for user with unknown role"""
        self.client.login(username='unknown', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/unknown_role.html')

    def test_employer_dashboard_context_data(self):
        """Test employer dashboard context contains correct data types"""
        self.client.login(username='employer', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        # Check that jobs are related to the employer
        jobs = response.context['jobs']
        for job in jobs:
            self.assertEqual(job.employer, self.employer)
        
        # Check that applications are related to employer's jobs
        applications = response.context['applications']
        for application in applications:
            self.assertEqual(application.job.employer, self.employer)

    def test_seeker_dashboard_context_data(self):
        """Test seeker dashboard context contains correct data types"""
        self.client.login(username='seeker', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        # Check that all applications belong to the seeker
        applications = response.context['applications']
        for application in applications:
            self.assertEqual(application.seeker, self.seeker)

    def test_employer_dashboard_with_no_jobs(self):
        """Test employer dashboard when employer has no jobs"""
        # Create new employer with no jobs
        new_employer = User.objects.create_user(
            username='newemployer',
            email='newemployer@test.com',
            password='testpass123',
            is_employer=True
        )
        
        self.client.login(username='newemployer', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['jobs'].count(), 0)
        self.assertEqual(response.context['applications'].count(), 0)

    def test_seeker_dashboard_with_no_applications(self):
        """Test seeker dashboard when seeker has no applications"""
        # Create new seeker with no applications
        new_seeker = User.objects.create_user(
            username='newseeker',
            email='newseeker@test.com',
            password='testpass123',
            is_seeker=True
        )
        
        self.client.login(username='newseeker', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['applications'].count(), 0)

    def test_dashboard_view_with_multiple_employers(self):
        """Test that employer only sees their own jobs and applications"""
        # Create another employer with jobs
        other_employer = User.objects.create_user(
            username='otheremployer',
            email='other@test.com',
            password='testpass123',
            is_employer=True
        )
        
        other_job = Job.objects.create(
            employer=other_employer,
            title='Other Job',
            description='Other Description',
            location='Other Location',
            salary=70000.00,
            published=True
        )
        
        Application.objects.create(
            job=other_job,
            seeker=self.seeker,
            status='Pending'
        )
        
        # Login as original employer
        self.client.login(username='employer', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        # Should only see own jobs
        jobs = response.context['jobs']
        for job in jobs:
            self.assertEqual(job.employer, self.employer)
            self.assertNotEqual(job.employer, other_employer)
        
        # Should only see applications to own jobs
        applications = response.context['applications']
        for application in applications:
            self.assertEqual(application.job.employer, self.employer)

    def test_dashboard_view_with_different_application_statuses(self):
        """Test dashboard shows applications with different statuses"""
        # Create applications with different statuses
        Application.objects.create(
            job=self.job1,
            seeker=self.seeker,
            status='Rejected'
        )
        
        self.client.login(username='employer', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        applications = response.context['applications']
        statuses = [app.status for app in applications]
        
        self.assertIn('Pending', statuses)
        self.assertIn('Accepted', statuses)
        self.assertIn('Rejected', statuses)

    def test_dashboard_url_pattern(self):
        """Test dashboard URL pattern resolves correctly"""
        url = reverse('dashboard')
        self.assertEqual(url, '/dashboard/')

    def test_dashboard_view_performance_with_select_related(self):
        """Test dashboard view uses select_related for performance"""
        # Create many applications
        for i in range(10):
            seeker = User.objects.create_user(
                username=f'seeker{i}',
                email=f'seeker{i}@test.com',
                password='testpass123',
                is_seeker=True
            )
            Application.objects.create(
                job=self.job1,
                seeker=seeker,
                status='Pending'
            )
        
        self.client.login(username='employer', password='testpass123')
        
        # This test ensures the view executes without issues
        # In a real scenario, you'd measure query count
        with self.assertNumQueries(4):  # Adjust based on actual query count
            response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)

    def test_dashboard_user_attributes_exist(self):
        """Test dashboard view checks for user attribute existence"""
        # Test with employer
        self.client.login(username='employer', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Test with seeker
        self.client.login(username='seeker', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Test with user without role attributes
        self.client.login(username='unknown', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/unknown_role.html')


class DashboardContextTest(TestCase):
    """Test dashboard context data integrity"""

    def setUp(self):
        self.employer = User.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123',
            is_employer=True
        )
        
        self.job = Job.objects.create(
            employer=self.employer,
            title='Test Job',
            description='Test Description',
            location='Test Location',
            salary=50000.00,
            published=True
        )
        
        self.client = Client()

    def test_employer_dashboard_context_keys(self):
        """Test employer dashboard has required context keys"""
        self.client.login(username='employer', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        required_keys = ['jobs', 'applications']
        for key in required_keys:
            self.assertIn(key, response.context)

    def test_seeker_dashboard_context_keys(self):
        """Test seeker dashboard has required context keys"""
        seeker = User.objects.create_user(
            username='seeker',
            email='seeker@test.com',
            password='testpass123',
            is_seeker=True
        )
        
        self.client.login(username='seeker', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        required_keys = ['applications']
        for key in required_keys:
            self.assertIn(key, response.context)


class DashboardURLTest(TestCase):
    """Test dashboard URL configuration"""

    def test_dashboard_url_resolves(self):
        """Test dashboard URL resolves to correct view"""
        from dashboard.views import dashboard_view
        from django.urls import resolve
        
        resolved = resolve('/dashboard/')
        self.assertEqual(resolved.func, dashboard_view)

    def test_dashboard_url_name(self):
        """Test dashboard URL name works correctly"""
        url = reverse('dashboard')
        self.assertEqual(url, '/dashboard/')


class DashboardSecurityTest(TestCase):
    """Test dashboard security and access control"""

    def setUp(self):
        self.employer1 = User.objects.create_user(
            username='employer1',
            email='employer1@test.com',
            password='testpass123',
            is_employer=True
        )
        
        self.employer2 = User.objects.create_user(
            username='employer2',
            email='employer2@test.com',
            password='testpass123',
            is_employer=True
        )
        
        self.job1 = Job.objects.create(
            employer=self.employer1,
            title='Employer 1 Job',
            description='Description',
            location='Location',
            salary=50000.00,
            published=True
        )
        
        self.job2 = Job.objects.create(
            employer=self.employer2,
            title='Employer 2 Job',
            description='Description',
            location='Location',
            salary=60000.00,
            published=True
        )
        
        self.client = Client()

    def test_employer_cannot_see_other_employer_jobs(self):
        """Test employer cannot see other employer's jobs"""
        self.client.login(username='employer1', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        jobs = response.context['jobs']
        job_employers = [job.employer for job in jobs]
        
        # Should only see own jobs
        self.assertIn(self.employer1, job_employers)
        self.assertNotIn(self.employer2, job_employers)

    def test_employer_cannot_see_other_employer_applications(self):
        """Test employer cannot see applications to other employer's jobs"""
        seeker = User.objects.create_user(
            username='seeker',
            email='seeker@test.com',
            password='testpass123',
            is_seeker=True
        )
        
        # Create applications to both employers' jobs
        Application.objects.create(job=self.job1, seeker=seeker)
        Application.objects.create(job=self.job2, seeker=seeker)
        
        self.client.login(username='employer1', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        applications = response.context['applications']
        
        # Should only see applications to own jobs
        for application in applications:
            self.assertEqual(application.job.employer, self.employer1)
            self.assertNotEqual(application.job.employer, self.employer2)

    def test_login_required_decorator_works(self):
        """Test @login_required decorator prevents unauthorized access"""
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/')