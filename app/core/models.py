import uuid

from django.db import models
from django.forms import ValidationError
from django.urls import reverse

from core.management.utils.notification import email_verification


class XIAConfiguration(models.Model):
    """Model for XIA Configuration """
    publisher = models.CharField(default='edX', max_length=200,
                                 help_text='Enter the source file to extract '
                                           'data from.')
    source_metadata_schema = models.CharField(
        default='edX_source_validate_schema.json', max_length=200,
        help_text='Enter the edX '
                  'schema file')
    source_target_mapping = models.CharField(
        default='edX_p2881_target_metadata_schema.json', max_length=200,
        help_text='Enter the schema '
                  'file to map '
                  'target.')
    target_metadata_schema = models.CharField(
        default='p2881_target_validation_schema.json', max_length=200,
        help_text='Enter the target '
                  'schema file to '
                  'validate from.')

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('Configuration-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id}'

    def save(self, *args, **kwargs):
        if not self.pk and XIAConfiguration.objects.exists():
            raise ValidationError('There is can be only one XIAConfiguration '
                                  'instance')
        return super(XIAConfiguration, self).save(*args, **kwargs)


class XISConfiguration(models.Model):
    """Model for XIS Configuration """

    xis_api_endpoint = models.CharField(
        help_text='Enter the XIS API endpoint',
        max_length=200
    )

    def save(self, *args, **kwargs):
        if not self.pk and XISConfiguration.objects.exists():
            raise ValidationError('There can be only one XISConfiguration '
                                  'instance')
        return super(XISConfiguration, self).save(*args, **kwargs)


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


class ReceiverEmailConfiguration(models.Model):
    """Model for Email Configuration """

    email_address = models.EmailField(
        max_length=254,
        help_text='Enter email personas addresses to send log data',
        unique=True)

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('Configuration-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id}'

    def save(self, *args, **kwargs):
        email_verification(self.email_address)
        return super(ReceiverEmailConfiguration, self).save(*args, **kwargs)


class SenderEmailConfiguration(models.Model):
    """Model for Email Configuration """

    sender_email_address = models.EmailField(
        max_length=254,
        help_text='Enter sender email address to send log data from',
        default='openlxphost@gmail.com')

    def save(self, *args, **kwargs):
        if not self.pk and SenderEmailConfiguration.objects.exists():
            raise ValidationError('There is can be only one '
                                  'SenderEmailConfiguration instance')
        return super(SenderEmailConfiguration, self).save(*args, **kwargs)


class MetadataLedger(models.Model):
    """Model for MetadataLedger """

    METADATA_VALIDATION_CHOICES = [('Y', 'Yes'), ('N', 'No')]
    RECORD_ACTIVATION_STATUS_CHOICES = [('Active', 'A'), ('Inactive', 'I')]
    RECORD_TRANSMISSION_STATUS_CHOICES = [('Successful', 'S'), ('Failed', 'F'),
                                          ('Pending', 'P'), ('Ready', 'R')]

    metadata_record_inactivation_date = models.DateTimeField(blank=True,
                                                             null=True)
    metadata_record_uuid = models.UUIDField(primary_key=True,
                                            default=uuid.uuid4, editable=False)
    record_lifecycle_status = models.CharField(
        max_length=10, blank=True, choices=RECORD_ACTIVATION_STATUS_CHOICES)
    source_metadata = models.JSONField(blank=True)
    source_metadata_extraction_date = models.DateTimeField(auto_now_add=True)
    source_metadata_hash = models.CharField(max_length=200)
    source_metadata_key = models.TextField()
    source_metadata_key_hash = models.CharField(max_length=200)
    source_metadata_transformation_date = models.DateTimeField(blank=True,
                                                               null=True)
    source_metadata_validation_date = models.DateTimeField(blank=True,
                                                           null=True)
    source_metadata_validation_status = models.CharField(
        max_length=10, blank=True, choices=METADATA_VALIDATION_CHOICES)
    target_metadata = models.JSONField(default=dict)
    target_metadata_hash = models.CharField(max_length=200)
    target_metadata_key = models.TextField()
    target_metadata_key_hash = models.CharField(max_length=200)
    target_metadata_transmission_date = models.DateTimeField(blank=True,
                                                             null=True)
    target_metadata_transmission_status = models.CharField(
        max_length=10, blank=True, default='Ready',
        choices=RECORD_TRANSMISSION_STATUS_CHOICES)
    target_metadata_transmission_status_code = models.IntegerField(blank=True,
                                                                   null=True)
    target_metadata_validation_date = models.DateTimeField(blank=True,
                                                           null=True)
    target_metadata_validation_status = models.CharField(
        max_length=10, blank=True, choices=METADATA_VALIDATION_CHOICES)
