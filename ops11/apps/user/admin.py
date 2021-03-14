from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    # 显示
    list_display = (
        'pk',
        'username',
        'password',
        'phone',
        'staff_id',
        'job_status',
    )

    # 编辑布局
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'name')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('User Profile'), {'fields': ('phone', 'staff_id', 'job_status')}),
    )