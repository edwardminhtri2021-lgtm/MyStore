# ================= IMPORTS =================
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import ast

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from functools import wraps
from django.http import HttpResponse

# ================= DATASETS =================
from analysis.data import (
    load_data,           # products
    load_data_views,     # views
    load_data_likes,     # likes
    load_orders_items,   # orders_items
    load_rules,          # rules
    load_tweets,         # tweets
    load_sales           # sales/customers
)

# ================= LOAD DATA =================
products = load_data()              # products table
views_data = load_data_views()      # product views
likes_data = load_data_likes()      # product likes
orders_items = load_orders_items()  # order items
rules = load_rules()                # rules
tweets = load_tweets()              # tweets
customers = load_sales()            # customer sales info

# ================= FIX PRODUCTS =================
if 'product_id' not in products.columns:
    products['product_id'] = range(1, len(products) + 1)

if 'name' not in products.columns:
    products['name'] = [f"Product {pid}" for pid in products['product_id']]

if 'price' not in products.columns:
    products['price'] = [1000 * (pid % 100 + 1) for pid in products['product_id']]

if 'created_at' not in products.columns:
    products['created_at'] = pd.Timestamp.now()

products['price_display'] = products['price'].apply(lambda x: f"{x:,}₫")

# ================= MERGE ORDERS =================
orders_merged = orders_items.merge(
    products[['product_id', 'name', 'price', 'price_display', 'created_at']],
    on='product_id',
    how='left'
)

# ================= HELPER FUNCTION =================
def plot_to_base64(fig):
    buffer = BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    return base64.b64encode(image_png).decode('utf-8')


# ==================== DECORATOR ====================
def superuser_required(view_func):
    @login_required(login_url='/login/')
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('no_access')
        return view_func(request, *args, **kwargs)
    return wrapper


# ==================== COMMON VIEWS ====================
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


# ==================== STORE ANALYSIS ====================
# ==================== STORE ANALYSIS ====================
# ==================== STORE ANALYSIS VIEW =================
@superuser_required
def store_analysis(request):
    # ================= SUMMARY METRICS =================
    total_products = len(products)
    total_orders = orders_items['order_id'].nunique()

    # New products (last 7 days)
    new_products = products[products['created_at'] >= (pd.Timestamp.now() - pd.Timedelta(days=7))]

    # Top products by quantity ordered
    product_orders = orders_items.groupby('product_id')['quantity'].sum().reset_index()
    top_products = product_orders.merge(products[['product_id', 'name']], on='product_id', how='left')
    top_products = top_products.sort_values('quantity', ascending=False).head(5)

    # ================= PLOTS =================
    # 1️⃣ Top 5 products by views
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    sns.barplot(
        data=products.sort_values('views', ascending=False).head(5),
        x='name', y='views', ax=ax1
    )
    ax1.set_title('Top 5 Products by Views')
    views_plot = plot_to_base64(fig1)
    plt.close(fig1)

    # 2️⃣ Top 5 products by likes
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    sns.barplot(
        data=products.sort_values('likes', ascending=False).head(5),
        x='name', y='likes', ax=ax2
    )
    ax2.set_title('Top 5 Products by Likes')
    likes_plot = plot_to_base64(fig2)
    plt.close(fig2)

    # ================= CONTEXT =================
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'new_products': new_products.to_dict(orient='records'),
        'top_products': top_products.to_dict(orient='records'),
        'views_plot': views_plot,
        'likes_plot': likes_plot
    }

    return render(request, 'analysis/store_analysis.html', context)



# ==================== CAMPAIGN ANALYSIS ====================
@superuser_required
def campaign_analysis(request):
    try:
        # Use the already loaded datasets
        df = pd.DataFrame({
            "views": views_data['views'],
            "likes": likes_data['likes']
        })

        context = {
            "views_count": df['views'].count(),
            "likes_count": df['likes'].count(),
            "views_head": df['views'].head().tolist(),
            "likes_head": df['likes'].head().tolist(),
            "views_stats": df['views'].describe().to_frame().to_html(
                classes="table table-bordered", justify="left"
            ),
            "likes_stats": df['likes'].describe().to_frame().to_html(
                classes="table table-bordered", justify="left"
            ),
            "views_max": df['views'].max(),
            "views_min": df['views'].min(),
            "views_max_count": (df['views'] == df['views'].max()).sum(),
            "views_min_count": (df['views'] == df['views'].min()).sum(),
            "likes_median": df['likes'].median(),
            "likes_equal_median": (df['likes'] == df['likes'].median()).sum(),
            "likes_greater_median": (df['likes'] > df['likes'].median()).sum(),
            "likes_less_median": (df['likes'] < df['likes'].median()).sum(),
            "category_likes_head": (df['likes'] >= df['likes'].median()).astype(int).head().tolist(),
            "views_unique_count": df['views'].nunique(),
            "likes_unique_count": df['likes'].nunique(),
            "df_head": df.head().to_html(classes="table table-striped", index=False),
        }

        return render(request, "analysis/campaign_analysis.html", context)

    except Exception as e:
        return render(request, "analysis/campaign_analysis.html", {"error": str(e)})


# ==================== STORE CHART ====================
@superuser_required
def store_chart(request):
    try:
        if orders_items.empty:
            return render(request, 'analysis/store_chart.html', {'error': 'No order data available.'})

        product_counts = orders_items.groupby('product_id')['quantity'].sum()

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=product_counts.index.astype(str), y=product_counts.values, palette='viridis', ax=ax)
        ax.set_xlabel('Product ID')
        ax.set_ylabel('Total Quantity Ordered')
        ax.set_title('Total Quantity Ordered per Product')
        plt.xticks(rotation=45)
        plt.tight_layout()

        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        graph = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close(fig)

        return render(request, 'analysis/store_chart.html', {'graph': graph})
    except Exception as e:
        return render(request, 'analysis/store_chart.html', {'error': str(e)})


# ==================== RULES VIEW ====================
@superuser_required
def rules_view(request):
    try:
        def format_frozenset(fs_str):
            try:
                fs = ast.literal_eval(fs_str)
                return ', '.join(str(i) for i in fs)
            except:
                return fs_str

        rules_df = rules.copy()
        rules_df['antecedents'] = rules_df['antecedents'].apply(format_frozenset)
        rules_df['consequents'] = rules_df['consequents'].apply(format_frozenset)
        rules_list = rules_df.to_dict(orient='records')

        return render(request, 'analysis/rules.html', {'rules': rules_list})
    except Exception as e:
        return render(request, 'analysis/rules.html', {"error": str(e)})
