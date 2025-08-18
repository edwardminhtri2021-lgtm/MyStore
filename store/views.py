import datetime
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import F
from rest_framework import viewsets
from .models import Product, SubCategory
from .serializers import ProductSerializer
from xhtml2pdf import pisa
import os
from store.models import Order
from django.conf import settings


# Preload all subcategories for menus
subcategory_list = SubCategory.objects.all()
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

def search(request):
    query = request.GET.get('q', '')  # lấy từ input 'q'
    category_id = request.GET.get('category', '')  # lấy từ select 'category'

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)  # tìm tên sản phẩm chứa từ khóa

    if category_id and category_id != "Tất cả":
        products = products.filter(category_id=category_id)  # lọc theo category nếu chọn

    context = {
        'products': products,
        'query': query,
        'selected_category': category_id,
        'subcategories': Category.objects.all(),  # để dropdown category còn hiển thị
    }
    return render(request, 'store/search_results.html', context)

@login_required
def wishlist(request):
    wishlist = request.session.get('wishlist', [])
    wishlist = [int(pid) for pid in wishlist]  # convert tất cả về int
    products = Product.objects.filter(id__in=wishlist)
    return render(request, 'store/wishlist.html', {'products': products})

@login_required
def add_to_wishlist(request, product_id):
    wishlist = request.session.get('wishlist', [])
    product_id = int(product_id)
    if product_id not in wishlist:
        wishlist.append(product_id)
        request.session['wishlist'] = wishlist

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Nếu là nút lớn (Ajax), trả JSON để cập nhật badge
        return JsonResponse({'success': True, 'count': len(wishlist)})
    else:
        # Nếu là nút nhỏ (thường click link), redirect qua wishlist
        return redirect('store:wishlist')

@login_required
def remove_from_wishlist(request, product_id):
    wishlist = request.session.get('wishlist', [])
    if product_id in wishlist:
        wishlist.remove(product_id)
        request.session['wishlist'] = wishlist

    # Kiểm tra Ajax request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'count': len(wishlist)})

    return redirect('store:wishlist')

# 1. Trang tài khoản
def account(request):
    return render(request, "store/account.html")

# 2. Trang đăng ký
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Mật khẩu không khớp!")
            return redirect("store:register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Tên đăng nhập đã tồn tại!")
            return redirect("store:register")

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        login(request, user)  # tự động đăng nhập sau khi đăng ký
        messages.success(request, "Đăng ký thành công!")
        return redirect("store:account")

    return render(request, "store/register.html")

# 3. Trang giới thiệu
def about(request):
    return render(request, "store/about.html")

# 4. Trang chính sách
def policy(request):
    return render(request, "store/policy.html")

# 5. Trang trợ giúp
def help_page(request):  # dùng help_page để tránh trùng với built-in "help"
    return render(request, "store/help.html")

def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'store/category_products.html', {'category': category, 'products': products})

# -------- AUTH (ĐĂNG NHẬP / ĐĂNG XUẤT) --------
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Đăng nhập
def log_in(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Lưu quyền superuser vào session
            request.session['superuser'] = user.is_superuser
            return redirect('index')  # chuyển về trang index
        else:
            return render(request, 'store/login.html', {
                'error': 'Sai username hoặc mật khẩu!'
            })
    return render(request, 'store/login.html')


def logout_view(request):
    logout(request)
    return redirect('/')   # safe redirect to homepage

def logout_success(request):
    return render(request, 'store/logout.html')

# Trang chính (chỉ vào được khi đã đăng nhập)
@login_required
def index(request):
    superuser = request.session.get('superuser', False)
    return render(request, 'store/index.html', {
        'superuser': superuser
    })



def remove_from_cart(request, product_id):
    """Remove product from cart (session-based cart)."""
    cart = request.session.get('cart', {})

    product_id_str = str(product_id)
    if product_id_str in cart:
        del cart[product_id_str]  # Remove the item
        request.session['cart'] = cart
        request.session.modified = True  # Save session

    return redirect('store:cart')  # Redirect back to cart page

# store/views.py
def set_superuser(request):
    request.session['superuser'] = True
    return redirect('report_home')

def all_products(request):
    products = Product.objects.all()
    return render(request, 'store/all_products.html', {'products': products})

# ---------------- REST API VIEWSET ----------------
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


# ---------------- CART FUNCTIONS ----------------
def add_to_cart(request, product_id):
    """Add product to cart using session storage."""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)

        # Get current cart from session or create an empty one
        cart = request.session.get('cart', {})

        product_id_str = str(product_id)
        cart[product_id_str] = cart.get(product_id_str, 0) + 1

        request.session['cart'] = cart
        request.session.modified = True  # Force save session
        print('Cart session:', request.session['cart'])

        return redirect('store:cart')  # Ensure this URL name is defined

    return redirect('store:shop', 0)  # Redirect to shop if not POST


def cart_view(request):
    """Display cart page with all products in session."""
    cart = request.session.get('cart', {})
    cart_items, total = [], 0

    for product_id_str, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id_str)
            item_total = product.price * quantity
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total,
            })
        except Product.DoesNotExist:
            continue  # Skip deleted products

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total_price': total,
        'subcategories': subcategory_list,
    })


# ---------------- MAIN PAGES ----------------
def index(request):
    """Home page showing newest and most viewed products."""
    tbgd = SubCategory.objects.filter(category=1)
    ddnb = SubCategory.objects.filter(category=2)
    product_list = Product.objects.order_by("-public_day")

    context = {
        'newest': product_list.first(),
        'twenty_newest': product_list[:20],
        'most_viewed_list': Product.objects.order_by("-viewed")[:3],
        'subcategories': subcategory_list,
        'tbgd': tbgd,
        'ddnb': ddnb
    }
    return render(request, "store/index.html", context)


def shop(request, pk=None):
    if pk:  # lọc theo category
        products = Product.objects.filter(category_id=pk)
    else:   # tất cả sản phẩm
        products = Product.objects.all()
    
    return render(request, "store/shop.html", {
        "products": products,
        "subcategory_name": Category.objects.get(pk=pk).name if pk else "Tất cả",
    })

import os
import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import Product

# ----- Load orders_items.csv và tính số lần mua từng sản phẩm 1 lần khi server khởi động -----
orders_file = os.path.join(settings.BASE_DIR, 'media/analysis/orders_items.csv')

product_counts = pd.Series(dtype=int)  # Series rỗng ban đầu

if os.path.exists(orders_file):
    df = pd.read_csv(orders_file, dtype={'product_id': int})
    # Đếm số lần xuất hiện của từng product_id
    product_counts = df['product_id'].value_counts()
    print("Loaded product counts for", len(product_counts), "products")
else:
    print("Orders file not found:", orders_file)

# ----- Hàm gợi ý sản phẩm phổ biến -----
def suggest_products(top_n=5):
    # Lấy top_n product_id theo số lần mua nhiều nhất
    top_products = product_counts.head(top_n).index.tolist()
    return top_products

# ----- View product_detail -----
def product_detail(request, pk):
    # Lấy sản phẩm, nếu không có sẽ trả 404
    product = get_object_or_404(Product, pk=pk)

    # Lấy danh sách sản phẩm phổ biến gợi ý
    suggested_ids = suggest_products(top_n=5)
    list_asc_products = Product.objects.filter(pk__in=suggested_ids).exclude(pk=pk)

    return render(request, 'store/product.html', {
        'product': product,
        'list_asc_products': list_asc_products
    })

# ---------------- OTHER PAGES ----------------
def cart(request):
    return render(request, 'store/cart.html', {'subcategories': subcategory_list})


def checkout(request):
    return render(request, 'store/checkout.html', {'subcategories': subcategory_list})


def contact(request):
    return render(request, 'store/contact.html', {'subcategories': subcategory_list})


def show_base(request):
    return render(request, 'store/base.html')
