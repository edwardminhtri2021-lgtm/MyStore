from rest_framework import serializers
from .models import Product  # Assuming you have a Product model

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
