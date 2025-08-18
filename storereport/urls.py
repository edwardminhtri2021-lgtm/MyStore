from django.urls import path
from . import views   # Use relative import for views.py

app_name = 'storereport'

urlpatterns = [
    path('', views.report_home, name='home'),
    path('quarter/', views.report_in_quarter, name='quarter'),
]
