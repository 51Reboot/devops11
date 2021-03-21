from django.contrib import admin

from .models import Publisher
from .models import Book
# Register your models here.


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    # 显示
    list_display = (
        'pk',
        'name',
        'address',
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # 显示
    list_display = (
        'pk',
        'name',
        'publisher',
        'publisher_state',
        # 'authors',
        'price',
        'remark',
    )
