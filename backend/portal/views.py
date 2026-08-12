

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from .forms import AdmissionForm

# We will import models inside the methods to prevent "ImportError" loops
class HomeView(TemplateView):
    template_name = 'portal/home.html'
    
    def get_context_data(self, **kwargs):
        from .models import Course  # Local import
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.filter(is_active=True)[:6]
        return context

class AdmissionView(FormView):
    template_name = 'portal/admission.html'
    form_class = AdmissionForm
    success_url = reverse_lazy('admission_success')
    
    def form_valid(self, form):
        try:
            student = form.save()
            messages.success(self.request, f'Submission successful! ID: {student.id}')
            return super().form_valid(form)
        except Exception:
            messages.error(self.request, 'An error occurred during submission.')
            return self.form_invalid(form)

class AdmissionSuccessView(TemplateView):
    template_name = 'portal/admission_success.html'

class CoursesView(TemplateView):
    template_name = 'portal/courses.html'
    
    def get_context_data(self, **kwargs):
        from .models import Course  # Local import
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.filter(is_active=True)
        return context

class AboutView(TemplateView):
    template_name = 'portal/about.html'

class ContactView(TemplateView):
    template_name = 'portal/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            from .models import Branch
            context['branches'] = Branch.objects.filter(is_active=True)
        except ImportError:
            context['branches'] = []
        return context
    