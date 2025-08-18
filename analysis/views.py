import os
import io
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import F
from django.contrib.auth.decorators import login_required

from store.models import Order, OrderItem, Product

# ==================== DECORATOR ====================
from functools import wraps

def superuser_required(view_func):
    """
    Decorator để chặn người dùng không phải superuser.
    Bắt buộc login, nếu không phải superuser sẽ redirect sang no_access.
    """
    @login_required(login_url='/login/')
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('no_access')
        return view_func(request, *args, **kwargs)
    return wrapper

# ==================== COMMON ====================
def no_access(request):
    return render(request, 'analysis/no_access.html')

from django.urls import reverse
from django.shortcuts import render

def index(request):
    links = [
        {"name": "Campaign Analysis", "url": reverse("analysis:campaign_analysis")},
        {"name": "Store Analysis", "url": reverse("analysis:store_analysis")},
        {"name": "Store Chart", "url": reverse("analysis:store_chart")},
        {"name": "Rules View", "url": reverse("analysis:store_rules")},  # <-- đúng tên mới
    ]
    return render(request, "analysis/index.html", {"links": links})



# ==================== CAMPAIGN ANALYSIS ====================
@superuser_required
def campaign_analysis(request):
    data_path = os.path.join(settings.MEDIA_ROOT, "analysis")

    # Đọc dữ liệu CSV
    views = pd.read_csv(os.path.join(data_path, "data_views.csv"))["views"]
    likes = pd.read_csv(os.path.join(data_path, "data_likes.csv"))["likes"]

    df = pd.DataFrame({"views": views, "likes": likes})

    # ==== 1. Thông tin cơ bản ====
    views_count = views.count()
    likes_count = likes.count()
    views_head = views.head().tolist()
    likes_head = likes.head().tolist()

    # ==== 2. Thống kê chung (hiển thị dạng bảng HTML) ====
    views_stats = views.describe().to_frame().to_html(classes="table table-bordered", justify="left")
    likes_stats = likes.describe().to_frame().to_html(classes="table table-bordered", justify="left")

    # ==== 3. Views max/min ====
    views_max = views.max()
    views_min = views.min()
    views_max_count = (views == views_max).sum()
    views_min_count = (views == views_min).sum()

    # ==== 4. Likes median ====
    likes_median = likes.median()
    likes_equal_median = (likes == likes_median).sum()
    likes_greater_median = (likes > likes_median).sum()
    likes_less_median = (likes < likes_median).sum()

    # ==== 5. Category likes ====
    category_likes = (likes >= likes_median).astype(int)
    category_likes_head = category_likes.head().tolist()

    # ==== 6. Unique count ====
    views_unique_count = views.nunique()
    likes_unique_count = likes.nunique()

    # ==== 7. DataFrame head ====
    df_head = df.head().to_html(classes="table table-striped", index=False)

    context = {
        "views_count": views_count,
        "likes_count": likes_count,
        "views_head": views_head,
        "likes_head": likes_head,
        "views_stats": views_stats,
        "likes_stats": likes_stats,
        "views_max": views_max,
        "views_min": views_min,
        "views_max_count": views_max_count,
        "views_min_count": views_min_count,
        "likes_median": likes_median,
        "likes_equal_median": likes_equal_median,
        "likes_greater_median": likes_greater_median,
        "likes_less_median": likes_less_median,
        "category_likes_head": category_likes_head,
        "views_unique_count": views_unique_count,
        "likes_unique_count": likes_unique_count,
        "df_head": df_head,
    }

    return render(request, "analysis/campaign_analysis.html", context)

# ==================== STORE ANALYSIS ====================
@superuser_required
def store_analysis(request):
    # Load products
    products = Product.objects.all()
    total_products = products.count()
    
    # Lấy 5 sản phẩm mới nhất
    new_products = products.order_by('-public_day')[:5] if 'public_day' in [f.name for f in Product._meta.fields] else products[:5]
    
    # Load orders
    orders = Order.objects.all()
    total_orders = orders.count()
    
    # Load order items và tính giá
    order_items = OrderItem.objects.annotate(
        price=F('product__price'),
        total_price_item=F('quantity') * F('product__price')
    ).values(
        'id', 'order_id', 'product_id', 'quantity', 'price', 'total_price_item'
    )
    
    context = {
        "products": products,
        "new_products": new_products,
        "total_products": total_products,
        "orders": orders,
        "total_orders": total_orders,
        "order_items": order_items,
    }
    
    return render(request, "analysis/store_analysis.html", context)

# ==================== STORE CHART ====================
def plot_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)
    return image_base64

@superuser_required
def store_chart(request):
    try:
        df = pd.read_csv('media/analysis/orders_items.csv')
    except FileNotFoundError:
        return render(request, 'analysis/store_chart.html', {'error': 'File orders_items.csv không tồn tại.'})

    df['product_id'] = df['product_id'].astype(str)

    if 'quantity' in df.columns:
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)
        product_counts = df.groupby('product_id')['quantity'].sum()
    else:
        product_counts = df['product_id'].value_counts()

    if product_counts.empty:
        product_counts = pd.Series([1], index=['No Data'])

    plt.figure(figsize=(10, 6))
    sns.barplot(x=product_counts.index, y=product_counts.values, palette='viridis')
    plt.xlabel('Product ID')
    plt.ylabel('Số lượng đã đặt')
    plt.title('Số lượng hàng hóa đã đặt theo từng Product')
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    graph = base64.b64encode(image_png).decode('utf-8')

    context = {'graph': graph}
    return render(request, 'analysis/store_chart.html', context)

# ==================== RULES ====================
@superuser_required
def rules_view(request):
    rules_file = 'media/analysis/rules.csv'
    rules_df = pd.read_csv(rules_file)

    def format_frozenset(fs_str):
        try:
            fs = eval(fs_str)
            return ', '.join(str(i) for i in fs)
        except:
            return fs_str

    rules_df['antecedents'] = rules_df['antecedents'].apply(format_frozenset)
    rules_df['consequents'] = rules_df['consequents'].apply(format_frozenset)

    rules_list = rules_df.to_dict(orient='records')

    return render(request, 'analysis/rules.html', {'rules': rules_list})
