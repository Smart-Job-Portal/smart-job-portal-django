from django import forms
from .models import Application
from django.core.exceptions import ValidationError

class ApplicationForm(forms.ModelForm):
    resume = forms.FileField(
        label="Upload Resume",
        help_text="Acceptable formats: PDF, DOC, DOCX. Max size: 5MB",
        widget=forms.FileInput(attrs={'accept': '.pdf,.doc,.docx', 'required': 'required'})
    )

    class Meta:
        model = Application
        fields = ['resume']

    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            # Validate file size (Max 5MB)
            if resume.size > 5 * 1024 * 1024:  
                
                raise ValidationError("The file size exceeds 5MB. Please upload a smaller file.")

            # Validate file format
            allowed_extensions = ['.pdf', '.doc', '.docx']
            filename = resume.name.lower()
           
            if not any(filename.endswith(ext) for ext in allowed_extensions):
                raise ValidationError(
                    f"Invalid file format. Only files with extensions {', '.join(allowed_extensions)} are allowed."
                )
        
        return resume

