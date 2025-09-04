from rest_framework import serializers
from jobs.models import Job, Application

class JobSerializer(serializers.ModelSerializer):
    employer = serializers.ReadOnlyField(source='employer.username')

    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ('employer', 'posted_on')

class ApplicationSerializer(serializers.ModelSerializer):
    seeker = serializers.ReadOnlyField(source='seeker.username')
    job_title = serializers.ReadOnlyField(source='job.title')

    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ('seeker', 'status', 'applied_on', 'job')
