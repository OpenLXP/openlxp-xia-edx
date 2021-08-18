from django.db import models
from django.forms import ValidationError


class XSRConfiguration(models.Model):
    """Model for XSR Configuration """

    xsr_api_endpoint = models.CharField(
        help_text='Enter the XSR API endpoint', max_length=200)
    token_url = models.CharField(
        help_text='Enter the token URL for edX', max_length=200)
    edx_client_id = models.CharField(
        help_text='Enter the edX client ID', max_length=200)
    edx_client_secret = models.CharField(
        help_text='Enter the edX client secret', max_length=500)

    def save(self, *args, **kwargs):
        if not self.pk and XSRConfiguration.objects.exists():
            raise ValidationError('There can be only one XISConfiguration '
                                  'instance')
        return super(XSRConfiguration, self).save(*args, **kwargs)
