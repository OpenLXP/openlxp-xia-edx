from django.contrib import admin

from .models import XSRConfiguration

# Register your models here.


@admin.register(XSRConfiguration)
class XSRConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        'xsr_api_endpoint',
        'token_url',
        'edx_client_id',
        'edx_client_secret',)
    fields = ['xsr_api_endpoint',
              'token_url',
              'edx_client_id',
              'edx_client_secret']
