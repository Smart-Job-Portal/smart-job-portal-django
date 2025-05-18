from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Job, Application
from django.http import HttpResponseForbidden
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin , UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from .forms import ApplicationForm
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger

class JobListView(ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    ordering = ['-posted_on']
    

    def get_queryset(self):
        queryset = Job.active_jobs.active().order_by('-posted_on')

        search_query = self.request.GET.get('search', None)
        location_filter = self.request.GET.get('location', None)  
        salary_filter = self.request.GET.get('salary', None)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(description__icontains=search_query)
            )
        
        if location_filter:
            queryset = queryset.filter(location__icontains=location_filter)

        if salary_filter:
            queryset = queryset.filter(salary__icontains=salary_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['empty_jobs'] = not self.get_queryset().exists()
        context['search_query'] = self.request.GET.get('search', '')
        context['location_filter'] = self.request.GET.get('location', '')  
        context['salary_filter'] = self.request.GET.get('salary', '') 
        return context

    def get(self, request, *args, **kwargs):
     
        self.object_list = self.get_queryset()
        paginator = Paginator(self.object_list, 2)
        page = request.GET.get('page', 1)

        try:
            jobs = paginator.page(page)
        except PageNotAnInteger:
            jobs = paginator.page(1)
        except EmptyPage:
            jobs = paginator.page(paginator.num_pages)
        except InvalidPage:
            jobs = paginator.page(1)

        context = self.get_context_data()
        context['jobs'] = jobs
        context['is_paginated'] = jobs.has_other_pages()
        context['page_obj'] = jobs

        return render(request, self.template_name, context)


class JobDetailView(DetailView):
    model = Job
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
      
        if self.request.user.is_authenticated and self.request.user == self.object.employer:
            context['is_employer'] = True
        else:
            context['is_employer'] = False
        return context

class JobCreateView(LoginRequiredMixin, CreateView):
    model = Job
    template_name = 'jobs/job_form.html'
    fields = ['title', 'description', 'location', 'salary']  
    success_url = reverse_lazy('job_list')  

    def form_valid(self, form):
        form.instance.employer = self.request.user  
        return super().form_valid(form)


class JobUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Job
    template_name = 'jobs/job_form.html' 
    fields = ['title', 'description', 'location', 'salary']
    success_url = reverse_lazy('job_list')

    def test_func(self):
        job = self.get_object()
        return self.request.user == job.employer



class JobDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Job
    template_name = 'jobs/job_confirm_delete.html'  
    success_url = reverse_lazy('job_list')

    def test_func(self):
        job = self.get_object()
        return self.request.user == job.employer


@login_required
def apply_job(request, job_id):
    if not request.user.is_seeker:  
        return HttpResponseForbidden("You are not allowed to apply for jobs.")

    job = get_object_or_404(Job, id=job_id)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.seeker = request.user
            application.status = 'Pending'
            application.save()
            return redirect('job_list')
        else:
            
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


@login_required
def accept_application(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    
    if not hasattr(request.user, 'is_employer') or not request.user.is_employer:
        return HttpResponseForbidden("You must be an employer.")
    if application.job.employer != request.user:
        return HttpResponseForbidden("You can only manage your own job applications.")
    if request.method == "POST":
        application.status = 'Accepted'
        application.save()
    return redirect('dashboard')  

@login_required
def reject_application(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    if not hasattr(request.user, 'is_employer') or not request.user.is_employer:
        return HttpResponseForbidden("You must be an employer.")
    if application.job.employer != request.user:
        return HttpResponseForbidden("You can only manage your own job applications.")
    if request.method == "POST":
        application.status = 'Rejected'
        application.save()
    return redirect('dashboard')