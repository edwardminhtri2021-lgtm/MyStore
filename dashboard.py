import streamlit as st
import pandas as pd
from django.conf import settings
import os
import django

# --- Thiết lập môi trường Django ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MyStore.settings")
django.setup()

from store.models import Order

# --- Tạo dataframe từ database ---
data = []
for order in Order.objects.all():
    total_quantity = sum(item.quantity for item in order.items.all())
    total_price = sum(item.total_price() for item in order.items.all())
    data.append({
        "OrderID": order.id,
        "Customer": order.customer_name,
        "Address": order.address,
        "Total Quantity": total_quantity,
        "Total Price": total_price
    })

df = pd.DataFrame(data)

# --- Streamlit layout ---
st.title("Dashboard MyStore - Chi tiết đơn hàng")

# Tùy chọn hiển thị cột
columns = st.multiselect("Click to Open Fields", df.columns.tolist(), default=df.columns.tolist())
st.dataframe(df[columns])

# Biểu đồ cột: số lượng và tổng tiền
st.subheader("Biểu đồ cột theo đơn hàng")
st.bar_chart(df.set_index("OrderID")[["Total Quantity", "Total Price"]])

# Xuất báo cáo
st.subheader("Xuất báo cáo")
export_format = st.selectbox("Chọn định dạng", ["CSV", "Excel", "HTML"])
if st.button("Xuất báo cáo"):
    if export_format == "CSV":
        df.to_csv("order_summary.csv", index=False)
        st.success("Đã xuất order_summary.csv")
    elif export_format == "Excel":
        df.to_excel("order_summary.xlsx", index=False)
        st.success("Đã xuất order_summary.xlsx")
    elif export_format == "HTML":
        df.to_html("order_summary.html", index=False)
        st.success("Đã xuất order_summary.html")
