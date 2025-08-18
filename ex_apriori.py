import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

# Đọc dữ liệu
df = pd.read_csv('media/analysis/orders_items.csv')

# Nhóm theo order_id và product_id, tính tổng quantity
basket = df.groupby(['order_id', 'product_id'])['quantity'].sum().unstack().fillna(0)

# Chuyển quantity >0 thành 1 (biểu thị sản phẩm được đặt)
basket_sets = basket.applymap(lambda x: 1 if x > 0 else 0)

# Áp dụng thuật toán Apriori
frequent_itemsets = apriori(basket_sets, min_support=0.01, use_colnames=True)

# Sinh luật kết hợp
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)

# Lưu kết quả ra file CSV
rules.to_csv('media/analysis/rules.csv', index=False)

print("Apriori completed. Rules saved to media/analysis/rules.csv")
