import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from pathlib import Path
from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse
from django.db.models import F
from django.contrib.auth.decorators import login_required
from functools import wraps

from store.models import Order, OrderItem, Product

# ==================== DECORATOR ====================
def superuser_required(view_func):
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

def index(request):
    links = [
        {"name": "Campaign Analysis", "url": reverse("analysis:campaign_analysis")},
        {"name": "Store Analysis", "url": reverse("analysis:store_analysis")},
        {"name": "Store Chart", "url": reverse("analysis:store_chart")},
        {"name": "Rules View", "url": reverse("analysis:store_rules")},
    ]
    return render(request, "analysis/index.html", {"links": links})

# Base path for CSV files
DATA_PATH = r"D:\MyStore\MyStore\analysis\data"

# ==================== CAMPAIGN ANALYSIS ====================
@superuser_required
def campaign_analysis(request):
    views_csv = os.path.join(DATA_PATH, "data_views.csv")
    likes_csv = os.path.join(DATA_PATH, "data_likes.csv")

    views = pd.read_csv(views_csv)["views"]
    likes = pd.read_csv(likes_csv)["likes"]

    df = pd.DataFrame({"views": views, "likes": likes})

    context = {
        "views_count": views.count(),
        "likes_count": likes.count(),
        "views_head": views.head().tolist(),
        "likes_head": likes.head().tolist(),
        "views_stats": views.describe().to_frame().to_html(classes="table table-bordered", justify="left"),
        "likes_stats": likes.describe().to_frame().to_html(classes="table table-bordered", justify="left"),
        "views_max": views.max(),
        "views_min": views.min(),
        "views_max_count": (views == views.max()).sum(),
        "views_min_count": (views == views.min()).sum(),
        "likes_median": likes.median(),
        "likes_equal_median": (likes == likes.median()).sum(),
        "likes_greater_median": (likes > likes.median()).sum(),
        "likes_less_median": (likes < likes.median()).sum(),
        "category_likes_head": (likes >= likes.median()).astype(int).head().tolist(),
        "views_unique_count": views.nunique(),
        "likes_unique_count": likes.nunique(),
        "df_head": df.head().to_html(classes="table table-striped", index=False),
    }

    return render(request, "analysis/campaign_analysis.html", context)

# ==================== STORE ANALYSIS ====================
@superuser_required
def store_analysis(request):
    products = Product.objects.all()
    total_products = products.count()
    new_products = products.order_by('-public_day')[:5] if 'public_day' in [f.name for f in Product._meta.fields] else products[:5]
    
    orders = Order.objects.all()
    total_orders = orders.count()

    order_items = OrderItem.objects.annotate(
        price=F('product__price'),
        total_price_item=F('quantity') * F('product__price')
    ).values('id', 'order_id', 'product_id', 'quantity', 'price', 'total_price_item')
    
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
    # Use MEDIA_ROOT so it's easier to configure
    DATA_PATH = os.path.join(settings.BASE_DIR, 'MyStore', 'analysis', 'data')
    file_path = os.path.join(DATA_PATH, 'orders_items.csv')


    try:
        df = pd.read_csv(file_path)
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

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=product_counts.index, y=product_counts.values, palette='viridis', ax=ax)
    ax.set_xlabel('Product ID')
    ax.set_ylabel('Số lượng đã đặt')
    ax.set_title('Số lượng hàng hóa đã đặt theo từng Product')
    plt.xticks(rotation=45)

    graph = plot_to_base64(fig)

    return render(request, 'analysis/store_chart.html', {'graph': graph})

# ==================== RULES ====================
@superuser_required
def rules_view(request):
    rules_csv = os.path.join(DATA_PATH, "rules.csv")
    rules_df = pd.read_csv(rules_csv)

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


