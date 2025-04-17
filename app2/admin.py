from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Recipe, Testimonial, User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    actions = ['make_admin', 'remove_admin']

    def make_admin(self, request, queryset):
        queryset.update(is_staff=True)
        self.message_user(request, "Selected users have been made admins")
    make_admin.short_description = "Make selected users admins"

    def remove_admin(self, request, queryset):
        queryset.update(is_staff=False, is_superuser=False)
        self.message_user(request, "Admin privileges removed from selected users")
    remove_admin.short_description = "Remove admin privileges"

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'preparation_time', 'difficulty', 'rating')
    list_filter = ('category', 'difficulty')
    search_fields = ('title', 'description', 'tags')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_title', 'rating', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user_title', 'content')
    list_filter = ('rating', 'created_at')
    ordering = ('-created_at',)
    
    actions = ['delete_selected']

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and request.method == 'GET'

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            actions.pop('delete_selected', None)
        return actions