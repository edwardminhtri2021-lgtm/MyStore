import os
import django
import pandas as pd

# Thiết lập Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MyStore.settings")
django.setup()

from store.models import Order

# Lấy dữ liệu từ database
data = []
for order in Order.objects.all():
    data.append({
        'OrderID': order.id,
        'Customer': order.customer_name,
        'Address': order.address,
        'TotalPrice': order.total_price,
        'CreatedAt': order.created_at
    })

# Chuyển thành DataFrame
df = pd.DataFrame(data)

# In ra console
print(df)

# Xuất ra các định dạng khác nhau
df.to_csv("order_summary.csv", index=False)
df.to_excel("order_summary.xlsx", index=False)
df.to_html("order_summary.html", index=False)

print("Báo cáo đã được xuất thành công!")
