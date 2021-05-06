from django.contrib import admin

from .models import (DeleteEmailConfiguration, EmailConfiguration,
                     SenderEmailConfiguration, XIAConfiguration)

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


@admin.register(EmailConfiguration)
class EmailConfigurationAdmin(admin.ModelAdmin):
    list_display = ('email_address',)


@admin.register(SenderEmailConfiguration)
class SenderEmailConfigurationAdmin(admin.ModelAdmin):
    list_display = ('sender_email_address',)


@admin.register(DeleteEmailConfiguration)
class DeleteEmailConfigurationAdmin(admin.ModelAdmin):
    list_display = ('delete_email_address',)
