import os
from django.core.wsgi import get_wsgi_application

# Trỏ tới file settings của project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyStore.settings')

# Tạo WSGI application
application = get_wsgi_application()
