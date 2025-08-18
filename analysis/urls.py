# analysis/urls.py
from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    path('', views.index, name='index'),  # example view
    path("campaign_analysis/", views.campaign_analysis, name="campaign_analysis"),
    path("store_analysis/", views.store_analysis, name="store_analysis"),
    path('store_chart/', views.store_chart, name='store_chart'),
    path('store_rules/', views.rules_view, name='store_rules'),
    path('no-access/', views.no_access, name='no_access'),
]
