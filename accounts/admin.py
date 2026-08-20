from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    model = User

    list_display = (
        'email',
        'name',
        'role',
        'status',
        'is_staff',
        'created_at',
    )

    list_filter = (
        'role',
        'status',
        'is_staff',
    )

    ordering = ('-created_at',)

    search_fields = (
        'email',
        'name',
    )

    fieldsets = (
        (None, {
            'fields': (
                'email',
                'password',
            )
        }),
        ('Personal Information', {
            'fields': (
                'name',
            )
        }),
        ('Role & Status', {
            'fields': (
                'role',
                'status',
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'name',
                'password1',
                'password2',
                'role',
                'status',
                'is_staff',
                'is_superuser',
            ),
        }),
    )