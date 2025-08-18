from django.urls import path
from . import views

app_name = 'khach-hang'
urlpatterns = [
    path('', views.index, name='index.html'),
    path('dang-ky.html', views.dang_ky, name='dang-ky.html'),
    path('dang-nhap.html', views.dang_nhap, name='dang-nhap.html'),
    path('dang-xuat.html', views.dang_xuat, name='dang-xuat.html'),
    path('dat-hang.html', views.dat_hang, name='dat-hang.html'),
]