from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Language, InputTranslation, OutputTranslation

admin.site.register(CustomUser, UserAdmin)
