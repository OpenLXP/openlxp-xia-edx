from django.contrib import admin

from .models import (ReceiverEmailConfiguration, SenderEmailConfiguration,
                     XIAConfiguration, XISConfiguration, XSRConfiguration)

# Register your models here.


@admin.register(XIAConfiguration)
class XIAConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        'publisher',
        'source_metadata_schema',
        'source_target_mapping',
        'target_metadata_schema',)
    fields = ['publisher',
              'source_metadata_schema',
              'source_target_mapping',
              'target_metadata_schema']


@admin.register(XISConfiguration)
class XISConfigurationAdmin(admin.ModelAdmin):
    list_display = ('xis_api_endpoint',)
    fields = ['xis_api_endpoint']


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


@admin.register(ReceiverEmailConfiguration)
class ReceiverEmailConfigurationAdmin(admin.ModelAdmin):
    list_display = ('email_address',)


@admin.register(SenderEmailConfiguration)
class SenderEmailConfigurationAdmin(admin.ModelAdmin):
    list_display = ('sender_email_address',)
