from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Job, Application
from django.http import HttpResponseForbidden

from django.views.generic import ListView
from .models import Job
from django.views.generic import DetailView

from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Job

from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy


from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .forms import ApplicationForm


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Job, Application


from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger

class JobListView(ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    ordering = ['posted_on']
    

    def get_queryset(self):
        queryset = Job.objects.all().order_by('posted_on')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # If no jobs exist, set an `empty_jobs` flag
        context['empty_jobs'] = not self.get_queryset().exists()
        return context

    def get(self, request, *args, **kwargs):
        # Retrieve the full queryset
        self.object_list = self.get_queryset()

        # Set up the Paginator
        paginator = Paginator(self.object_list, 2)

        # Get the requested page number
        page = request.GET.get('page', 1)

        try:
            # Make sure we have a valid page
            jobs = paginator.page(page)
        except PageNotAnInteger:
            # Non-integer: Default to the first page.
            jobs = paginator.page(1)
        except EmptyPage:
            # Out-of-range or negative page: Go to the last page.
            jobs = paginator.page(paginator.num_pages)
        except InvalidPage:
            # Catch unexpected cases of invalid pages and default to the first.
            jobs = paginator.page(1)

        # Pass pagination and jobs info to the template context
        context = self.get_context_data()
        context['jobs'] = jobs
        context['is_paginated'] = jobs.has_other_pages()
        context['page_obj'] = jobs

        return render(request, self.template_name, context)


class JobDetailView(DetailView):
    model = Job
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'  # Default is object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if the user is the employer of the job
        if self.request.user.is_authenticated and self.request.user == self.object.employer:
            context['is_employer'] = True
        else:
            context['is_employer'] = False
        return context

class JobCreateView(LoginRequiredMixin, CreateView):
    model = Job
    template_name = 'jobs/job_form.html'  # Create this template
    fields = ['title', 'description', 'location', 'salary']  # Fields to display in the form
    success_url = reverse_lazy('job_list')  # Redirect after successful creation

    def form_valid(self, form):
        form.instance.employer = self.request.user  # Set employer to the current user
        return super().form_valid(form)


class JobUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Job
    template_name = 'jobs/job_form.html'  # Reuse the form
    fields = ['title', 'description', 'location', 'salary']
    success_url = reverse_lazy('job_list')

    def test_func(self):
        job = self.get_object()
        return self.request.user == job.employer



class JobDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Job
    template_name = 'jobs/job_confirm_delete.html'  # Create this template
    success_url = reverse_lazy('job_list')

    def test_func(self):
        job = self.get_object()
        return self.request.user == job.employer


@login_required
def apply_job(request, job_id):
    if not request.user.is_seeker:  # Only job seekers can apply
        return HttpResponseForbidden("You are not allowed to apply for jobs.")

    job = get_object_or_404(Job, id=job_id)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.seeker = request.user
            application.save()
            return redirect('job_list')
        else:
            # Form is invalid
            return render(request, 'jobs/apply_job.html', {'job': job, 'form': form})
    else:
        form = ApplicationForm()

    return render(request, 'jobs/apply_job.html', {'job': job, 'form': form})


@login_required
def job_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)

    if not request.user.is_employer:
        return HttpResponseForbidden("Only employers can view applications.")

    applications = Application.objects.filter(job=job)
    return render(request, 'jobs/job_applications.html', {
        'job': job,
        'applications': applications
    })
