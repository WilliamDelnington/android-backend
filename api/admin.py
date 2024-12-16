from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserChangeForm, CustomUserCreationsForm

# Register your models here.
class CustomUserAdmin(UserAdmin):
    # Fields to display in the list view
    list_display = ("email", "username", "is_active", "is_staff", "is_superuser")
    # Fields to filter by in the list view
    list_filter = ("is_active", "is_staff", "is_superuser")
    # Fields to search for in the admin interface
    search_fields = ('email', 'username')
    # Fields to use as readonly
    readonly_fields = ('userId', 'last_login')

    # Fieldsets for organizing fields in the detail view
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login',)}),
    )

    # Fields to use when creating a new user in the admin interface
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

    # Ordering of the users in the admin list view
    ordering = ('email',)

    add_form = CustomUserCreationsForm
    form = CustomUserChangeForm

admin.site.register(CustomUser, CustomUserAdmin)