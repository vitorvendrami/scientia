
from django.contrib import admin

from .models import NetworkModel, GenerateEnvironment


@admin.register(NetworkModel)
class NetworkAdmin(admin.ModelAdmin):
    list_display = ['user', 'uuid']
    empty_value_display = "-empty-"


@admin.register(GenerateEnvironment)
class GenerateAdmin(admin.ModelAdmin):
    list_display = ['uuid',]
    empty_value_display = "-empty-"
