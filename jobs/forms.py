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

    # THIS METHOD MUST BE INSIDE THE CLASS
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            # Validate file size (Max 5MB)
            if resume.size > 5 * 1024 * 1024:  # 5MB limit
                # Use ValidationError instead of forms.ValidationError for clarity
                raise ValidationError("The file size exceeds 5MB. Please upload a smaller file.")

            # Validate file format
            allowed_extensions = ['.pdf', '.doc', '.docx']
            filename = resume.name.lower()
            # Check if any allowed extension is at the end of the filename
            if not any(filename.endswith(ext) for ext in allowed_extensions):
                raise ValidationError(
                    f"Invalid file format. Only files with extensions {', '.join(allowed_extensions)} are allowed."
                )
        # Make sure to return the cleaned data
        return resume

