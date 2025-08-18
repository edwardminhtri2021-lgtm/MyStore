from django.shortcuts import render
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import make_password, check_password
from .forms import FormCustumer, FormDonHang
from .models import Customer, DonHang, CTDonHang
from django.shortcuts import redirect
from store import models
from datetime import datetime
# Create your views here.
subcategory_list = models.SubCategory.objects.all()
subcategory = 0
search_str = ''

def index(request):
    return render(request, "khachhang/index.html")

def dang_ky(request):
    if request.method == "POST":
        form = FormCustumer(data=request.POST)
        
        if (form.is_valid() and form.cleaned_data['password'] == form.cleaned_data['confirm']):
            print("HOP LE 1 =======================================================")
            kh = form.save(commit=False)
            kh.password = make_password(kh.password)
            print(kh.password)
            print(kh.save())
    else:
        form = FormCustumer()

    username = request.session.get('username', 0)
    return render(request, 'khachhang/dangky.html',{'form': form})

def dat_hang(request):
    id=request.session.get('idkh', False)
    diachigiaohang =''
    if id==False:
        return redirect("khach-hang:dang-nhap.html")
    kh = Customer.objects.get(pk = id)
    if request.method == "POST":
        diachigiaohang = request.POST.get('diachigiaohang')
        frmDatHang = DonHang()
        frmDatHang.diachigiaohang = diachigiaohang
        frmDatHang.ngaydathang = datetime.now()
        frmDatHang.httt = 'Tiền mặt'
        frmDatHang.tongtien = 0
        frmDatHang.tamung = 0
        frmDatHang.conlai = 0
        frmDatHang.save()
    return render(request, 'khachhang/dathang.html',{'fullname': kh.fullname,'email': kh.email,'phone': kh.phone ,'diachigiaohang':diachigiaohang})

def dang_nhap(request):
    if request.method == "POST":
        _username = request.POST.get("username")
        _password = request.POST.get("password")
        kh = Customer.objects.get(username =_username)
        if kh is not None:  
            checkpassword=check_password(_password, kh.password)    
            if check_password:      
                request.session['kh'] = kh.fullname
                request.session['idkh'] = kh.id
                return redirect("store:index.html")
            else:
                print("Username: {} and password: {}".format(_username, _password))
                login_result = "Username hoặc password không chính xác!"
                return render(request, "khachhang/dangnhap.html", {'login_result': login_result, 'subcategories': subcategory_list,})
        else:
            print("Username: {} and password: {}".format(_username, _password))
            login_result = "Username hoặc password không chính xác!"
            return render(request, "khachhang/dangnhap.html", {'login_result': login_result, 'subcategories': subcategory_list,})
    else:
        return render(request, "khachhang/dangnhap.html", {'subcategories': subcategory_list})

def dang_xuat(request):    
    del request.session['kh']
    del request.session['idkh']
    return redirect("store:index.html")