# Smart Job Portal

A comprehensive Django-based job portal application that connects job seekers with employers. The platform allows employers to post job listings and manage applications, while job seekers can browse and apply for jobs.

## Features

### For Job Seekers
- User registration and email verification
- Browse and search job listings
- Filter jobs by title, description, location, and salary
- Apply to jobs with resume upload
- View application status in personal dashboard
- Secure file upload with validation (PDF, DOC, DOCX formats)

### For Employers
- Post new job listings
- Manage job postings (create, edit, delete)
- View and manage job applications
- Accept/reject applications
- Email notifications for new applications
- Admin approval workflow for job listings

### System Features
- Role-based authentication (Job Seeker/Employer)
- Email verification system
- Admin panel for job approval
- Responsive design
- Caching for improved performance
- Celery integration for background tasks
- Signal-based email notifications

## Technology Stack

- **Backend**: Django 5.0.4
- **Database**: SQLite (default), PostgreSQL/MySQL compatible
- **Task Queue**: Celery (configured but can be disabled)
- **Email**: Django Email Backend
- **File Storage**: Local filesystem
- **Caching**: Django Cache Framework
- **Frontend**: HTML, CSS, Bootstrap (templates not included in provided files)

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- Redis (optional, for Celery)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd smart-job-portal
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Additional Dependencies (Optional)

If you want to use Celery for background tasks:

```bash
pip install celery redis
```

### 5. Environment Configuration

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# For production
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Redis (if using Celery)
REDIS_URL=redis://localhost:6379/0
```

### 6. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

### 8. Create Media Directory

```bash
mkdir media
mkdir media/resumes
```

## Configuration

### Settings

Update your `settings.py` file with the following configurations:

```python
# Add these to your INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'jobs',
    'dashboard',
    'core',
]

# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Email Configuration (from .env)
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Login/Logout URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
```

### URLs Configuration

Update your main `urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('jobs/', include('jobs.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('', include('jobs.urls')),  # Root URL points to job listings
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Running the Application

### Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

### With Celery (Optional)

If you want to use background tasks:

1. Start Redis server:
```bash
redis-server
```

2. Start Celery worker (in a separate terminal):
```bash
celery -A your_project_name worker -l info
```

3. Start Django development server:
```bash
python manage.py runserver
```

## Usage

### User Registration

1. Navigate to `/accounts/register/`
2. Choose role (Job Seeker or Employer)
3. Fill in registration details
4. Check email for verification link
5. Click verification link to activate account

### For Employers

1. Log in to your account
2. Go to `/jobs/create/` to post a new job
3. Wait for admin approval (jobs are not published immediately)
4. Manage applications from your dashboard
5. Accept or reject applications

### For Job Seekers

1. Log in to your account
2. Browse jobs at `/jobs/`
3. Use search and filter options
4. Apply to jobs by uploading your resume
5. Track application status in your dashboard

### Admin Functions

1. Access admin panel at `/admin/`
2. Approve job listings in the Jobs section
3. Manage users and applications
4. Use bulk actions to approve multiple jobs

## API Endpoints

### Authentication
- `GET/POST /accounts/register/` - User registration
- `GET/POST /accounts/login/` - User login
- `POST /accounts/logout/` - User logout
- `GET /accounts/activate/<uidb64>/<token>/` - Account activation

### Jobs
- `GET /jobs/` - List all published jobs
- `GET /jobs/<id>/` - Job detail view
- `POST /jobs/create/` - Create new job (employers only)
- `PUT /jobs/<id>/update/` - Update job (employer only)
- `DELETE /jobs/<id>/delete/` - Delete job (employer only)
- `POST /jobs/<id>/apply/` - Apply to job (seekers only)

### Dashboard
- `GET /dashboard/` - User dashboard (role-based)

## File Structure

```
smart-job-portal/
├── accounts/           # User authentication and management
├── jobs/              # Job listings and applications
├── dashboard/         # User dashboards
├── core/              # Shared utilities and tasks
├── media/             # Uploaded files
├── templates/         # HTML templates (to be created)
├── static/           # Static files (to be created)
├── manage.py         # Django management script
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## Database Models

### CustomUser
- Extends Django's AbstractUser
- Additional fields: `is_employer`, `is_seeker`

### Job
- Fields: title, description, location, salary, employer, published status
- Manager: `active_jobs` for published jobs only

### Application
- Links job seekers to jobs
- Fields: resume file, status (Pending/Accepted/Rejected)
- Automatic email notifications

## Deployment

### Production Settings

Create a production settings file or update existing settings:

```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# Use PostgreSQL in production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'job_portal_db',
        'USER': 'db_user',
        'PASSWORD': 'db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Deployment Steps

1. **Collect Static Files**:
```bash
python manage.py collectstatic
```

2. **Run Migrations**:
```bash
python manage.py migrate
```

3. **Create Superuser**:
```bash
python manage.py createsuperuser
```

4. **Configure Web Server** (Apache/Nginx):
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /static/ {
        alias /path/to/your/project/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/your/project/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Platform-as-a-Service Deployment

#### Heroku
1. Install Heroku CLI
2. Create `Procfile`:
```
web: gunicorn your_project_name.wsgi
worker: celery -A your_project_name worker -l info
```

3. Add dependencies:
```bash
pip install gunicorn dj-database-url whitenoise
```

4. Update settings for Heroku:
```python
import dj_database_url
DATABASES['default'] = dj_database_url.config(conn_max_age=600)
```

5. Deploy:
```bash
git add .
git commit -m "Deploy to Heroku"
heroku create your-app-name
git push heroku main
heroku run python manage.py migrate
```

## Security Considerations

1. **File Uploads**: Validate file types and sizes
2. **Authentication**: Use strong passwords and email verification
3. **Authorization**: Role-based access control implemented
4. **CSRF Protection**: Enabled by default in Django
5. **SQL Injection**: Django ORM provides protection
6. **Email Security**: Use app passwords for Gmail

## Performance Optimization

1. **Caching**: Job listings are cached for 60 seconds
2. **Database**: Use `select_related()` for related objects
3. **File Storage**: Consider using cloud storage for production
4. **Static Files**: Use CDN for static assets
5. **Database Indexing**: Add indexes for frequently queried fields

## Troubleshooting

### Common Issues

1. **Email not sending**: Check email configuration in `.env`
2. **File upload errors**: Verify media directory permissions
3. **Database errors**: Run migrations with `python manage.py migrate`
4. **Import errors**: Ensure all dependencies are installed
5. **Permission denied**: Check user roles and permissions

### Debug Mode

Enable debug mode for development:
```python
DEBUG = True
```

Check Django logs and use Django Debug Toolbar for detailed debugging.


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the Django documentation for framework-specific issues

## Changelog

### Version 1.0
- Initial release
- User authentication with email verification
- Job posting and application system
- Admin approval workflow
- Email notifications
- Caching system
- File upload validation