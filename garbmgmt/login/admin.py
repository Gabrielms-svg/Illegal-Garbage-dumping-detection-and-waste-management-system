from django.contrib import admin
from .models import Normal_user, Authority_user  # import your models

admin.site.register(Normal_user)
admin.site.register(Authority_user)
