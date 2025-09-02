# Smart Job Portal (Advanced)

Welcome to the **Smart Job Portal**, an advanced Django-based platform designed to simulate the real-world complexity of job recruitment systems. This project provides students and developers with a hands-on experience of developing a full-stack web application using modern technologies, secure authentication systems, and scalable backend tools.

---

## Project Description

The **Smart Job Portal** allows users to register as **Job Seekers** or **Employers**. Employers can post and manage job listings, while Job Seekers can browse, search, and apply for jobs. Admins moderate content and approve job postings. This extended version introduces advanced backend and frontend features, including secure JWT authentication, Redis caching, social login, and real-time notifications.

---

## Learning Objectives

By working on this project, You will:

* Learn to build scalable Django apps with a multi-app architecture
* Implement secure authentication with JWT and HTTPS
* Integrate social authentication using Google
* Use Redis for caching and background job processing
* Track user actions and manage notifications
* Handle media uploads and image processing
* Work with Celery for asynchronous task handling
* Create responsive, interactive dashboards for different user roles

---

## Suggested Project Architecture (*It is not forced to follow this Architecture*)

```
smart_job_portal/
├── accounts/         # Auth, roles, social login
├── jobs/             # Job CRUD, applications
├── dashboard/        # Dashboards for seekers/employers
├── core/             # Utilities, email logic, caching
├── notifications/    # Notification system
├── media/            # Uploaded images, resumes
├── thumbnails/       # Generated profile thumbnails
├── static/           # CSS, JS, images
├── templates/        # HTML templates
├── logs/             # User action logs
├── manage.py
└── config/           # Settings (dev/prod), URLs
```

---

## Advanced Features

### API

* Create APIs to support key functionalities in addition to your existing application. (You may reimplement the entire application using Django REST Framework (DRF) if you wish, but it's *not required*.)
* Use JWT authentication

### Authentication

* Email verification & password reset via email ✅
* Social authentication using Google

### Redis & Celery

* Redis for caching job listings and throttling 
* Redis for caching Views, Template Fragments,and Low-level caching wherever is needed. 
* Celery for background tasks (e.g., sending emails, generating thumbnails) 

### Profile Management

* UserProfile model with image upload and resume✅
* Automatic thumbnail generation on profile picture upload

### Notifications & Logging

* Email + in-app notification system for job approvals and applications✅
* User activity tracking via middleware and logging models✅

### Messaging System

* Using Django messages framework (django.contrib.messages).✅
* Inform users about the result of specific actions, such as successfully creating an object in the database or
successfully submitting a form.✅
* Integrated in views like login, job posting, etc.✅

### HTTPS and Security

* Run server using HTTPS in development.


### Bonus Features

* Advanced search with elastic search
* Resume preview & download
* Dashboard analytics for employers

---