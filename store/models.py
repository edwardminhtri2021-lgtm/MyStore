from django.db import models
import datetime
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.
from django.db import models

class Order(models.Model):
    customer_name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.FloatField(default=0.0)

    def __str__(self):
        return f"Order {self.id} - {self.customer_name}"


class Story(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    
    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    name = models.CharField(max_length=150, unique=True)
    image = models.ImageField(upload_to="store/images", default="store/images/default.png")
    
    def __str__(self):
        return self.name

class Product(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.PROTECT)
    name = models.CharField(max_length=250)
    price = models.FloatField(default=0.0)
    price_origin = models.FloatField(null=True)
    image = models.ImageField(upload_to="store/images", default="store/images/default.png")
    content = RichTextUploadingField(blank=True, null=True)
    public_day = models.DateTimeField(default=datetime.datetime.now)
    viewed = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
