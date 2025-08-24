# make_data_py.py (fix version)
import gzip, base64

def encode_file(path):
    with open(path, "rb") as f:
        raw = f.read()
    return base64.b64encode(gzip.compress(raw)).decode("utf-8")

files = {
    "data": "data.csv",
    "data_views": "data_views.csv",
    "data_likes": "data_likes.csv",
    "orders_items": "orders_items.csv",
    "rules": "rules.csv",
    "tweets": "tweets_data_science.csv",
    "sales": "sales.csv",
}

encoded = {name: encode_file(path) for name, path in files.items()}

template = f"""import pandas as pd
import gzip, base64
from io import BytesIO

# ========== Encoded datasets ==========
_data_b64 = \"\"\"{encoded['data']}\"\"\"
_data_views_b64 = \"\"\"{encoded['data_views']}\"\"\"
_data_likes_b64 = \"\"\"{encoded['data_likes']}\"\"\"
_orders_items_b64 = \"\"\"{encoded['orders_items']}\"\"\"
_rules_b64 = \"\"\"{encoded['rules']}\"\"\"
_tweets_b64 = \"\"\"{encoded['tweets']}\"\"\"
_sales_b64 = \"\"\"{encoded['sales']}\"\"\"

def _decode(b64):
    return gzip.decompress(base64.b64decode(b64))

def load_data():
    return pd.read_csv(BytesIO(_decode(_data_b64)))

def load_data_views():
    return pd.read_csv(BytesIO(_decode(_data_views_b64)))

def load_data_likes():
    return pd.read_csv(BytesIO(_decode(_data_likes_b64)))

def load_orders_items():
    return pd.read_csv(BytesIO(_decode(_orders_items_b64)))

def load_rules():
    return pd.read_csv(BytesIO(_decode(_rules_b64)))

def load_tweets():
    return pd.read_csv(BytesIO(_decode(_tweets_b64)))

def load_sales():
    return pd.read_csv(BytesIO(_decode(_sales_b64)))
"""

with open("data.py", "w", encoding="utf-8") as f:
    f.write(template)

print("✅ Đã tạo xong data.py (dùng gzip+base64 cho tất cả dataset)")
