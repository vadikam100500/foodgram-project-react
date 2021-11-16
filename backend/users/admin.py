from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1',
                       'password2', 'first_name',
                       'last_name', 'email'),
        }),
    )


admin.site.unregister(Group)
