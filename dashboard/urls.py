from django.urls import path
from .views import choose_role_view, dashboard_view

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
       path('choose-role/', choose_role_view, name='choose_role'),
]
