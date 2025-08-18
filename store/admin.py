from django.contrib import admin
from django.db.models import F
from django.utils import timezone

from .models import Category, SubCategory, Product, Story, Order


# -----------------------
# ACTIONS DÙNG CHUNG
# -----------------------

def change_public_day(modeladmin, request, queryset):
    """Đặt public_day = hôm nay (theo timezone)."""
    queryset.update(public_day=timezone.localdate())
change_public_day.short_description = "Đặt ngày public thành hôm nay"


def change_viewed(modeladmin, request, queryset):
    """Tăng lượt xem lên 1."""
    queryset.update(viewed=F('viewed') + 1)
change_viewed.short_description = "Tăng số lượt xem thêm 1"


def reset_viewed(modeladmin, request, queryset):
    """Đặt lượt xem = 0."""
    queryset.update(viewed=0)
reset_viewed.short_description = "Reset lượt xem về 0"


def mark_orders_paid(modeladmin, request, queryset):
    """Đánh dấu paid = True cho các order được chọn."""
    queryset.update(paid=True)
mark_orders_paid.short_description = "Đánh dấu đã thanh toán"


# -----------------------
# CUSTOM FILTER: THÁNG HIỆN HÀNH
# -----------------------
class CurrentMonthFilter(admin.SimpleListFilter):
    title = "Tháng hiện hành"
    parameter_name = "current_month"

    def lookups(self, request, model_admin):
        return (('1', "Chỉ tháng hiện hành"),)

    def queryset(self, request, queryset):
        if self.value() == '1':
            today = timezone.localdate()
            first = today.replace(day=1)
            # tính ngày đầu tháng sau
            if first.month == 12:
                next_first = first.replace(year=first.year + 1, month=1, day=1)
            else:
                next_first = first.replace(month=first.month + 1, day=1)
            return queryset.filter(public_day__gte=first, public_day__lt=next_first)
        return queryset


# -----------------------
# STORY ADMIN
# -----------------------
@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'content')


# -----------------------
# PRODUCT ADMIN
# -----------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'public_day', 'viewed')
    list_filter = (
        CurrentMonthFilter,                       # lọc nhanh tháng hiện hành (custom)
        'subcategory',                            # lọc theo loại
        ('public_day', admin.DateFieldListFilter), # lọc theo ngày public
    )
    search_fields = ('name',)
    actions = [change_public_day, change_viewed, reset_viewed]


# -----------------------
# ORDER ADMIN
# -----------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'address', 'is_paid')  # dùng method is_paid
    search_fields = ('address',)
    actions = [mark_orders_paid]

    def is_paid(self, obj):
        """Hiển thị trạng thái thanh toán"""
        # nếu model Order có field 'paid', dùng obj.paid
        return getattr(obj, 'paid', False)
    is_paid.boolean = True
    is_paid.short_description = "Đã thanh toán"


# -----------------------
# CATEGORY & SUBCATEGORY ADMIN
# -----------------------
admin.site.register(Category)
admin.site.register(SubCategory)


# -----------------------
# TÙY CHỈNH GIAO DIỆN ADMIN
# -----------------------
admin.site.site_header = "MyStore Admin"
admin.site.site_title = "MyStore Admin"
admin.site.index_title = "Quản trị MyStore"
