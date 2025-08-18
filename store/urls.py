from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
router = DefaultRouter()
router.register(r'products', views.ProductViewSet)

app_name = 'store'

urlpatterns = [
    path("shop/", views.shop, name="shop"),  # khi không có category
    path("shop/<int:category_id>/", views.shop, name="shop_by_category"),  # khi có category
    path('products/', views.all_products, name='all_products'),  # <-- thêm dòng này
    path('product/<int:pk>/', views.product_detail, name='product.html'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout.html'),
    path('contact/', views.contact, name='contact.html'),
    path('api/', include(router.urls)),
    path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
        # URL logout bằng POST
    path('logout/', LogoutView.as_view(), name='logout'),

    # Trang logout thành công
    path('logout-success/', views.logout_success, name='logout_success'),
    path('category/<int:category_id>/', views.category_products, name='category_products'),
    path('', views.index, name='index'),
    path('account/', views.account, name='account'),      # My Account
    path('register/', views.register, name='register'),   # Đăng ký
    path('about/', views.about, name='about'),            # Giới thiệu
    path('policy/', views.policy, name='policy'),         # Chính sách
    path('help/', views.help_page, name='help'),          # Trợ giúp
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('search/', views.search, name='search'),

]

