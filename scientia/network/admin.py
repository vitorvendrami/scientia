
from django.contrib import admin
from .models import GenerateEnvironment

@admin.register(GenerateEnvironment)
class GenerateAdmin(admin.ModelAdmin):
    list_display = ['uuid',]
    empty_value_display = "-empty-"
