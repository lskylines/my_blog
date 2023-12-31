from django.contrib import admin
from .models import Profile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

#admin.site.register(Profile)

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "UserProfile"

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)



admin.site.unregister(User)
admin.site.register(User, UserAdmin)
