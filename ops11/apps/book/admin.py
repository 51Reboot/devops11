from django.contrib import admin

from .models import Publisher
# Register your models here.


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    # 显示
    list_display = (
        'pk',
        'name',
        'address',
    )
