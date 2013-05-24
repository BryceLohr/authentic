from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.conf import settings

from .nonce.models import Nonce

class NonceModelAdmin(admin.ModelAdmin):
    list_display = ("value", "context", "not_on_or_after")

admin.site.register(Nonce, NonceModelAdmin)
if settings.AUTH_USER_MODEL == 'authentic2.User':
    from models import User
    admin.site.register(User, UserAdmin)
