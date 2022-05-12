from django.core.exceptions import ValidationError
from django.test import TestCase, tag

from core.models import XSRConfiguration


@tag('unit')
class ModelTests(TestCase):

    def test_create_xsr_configuration(self):
        """Test that creating a new XSR Configuration entry is successful
        with defaults """
        xsr_api_endpoint = 'api/test_file'
        token_url = 'token_url'
        edx_client_id = 'edx_client_id'
        edx_client_secret = 'edx_client_secret'

        xiaConfig = XSRConfiguration(
            xsr_api_endpoint=xsr_api_endpoint,
            token_url=token_url,
            edx_client_id=edx_client_id,
            edx_client_secret=edx_client_secret)

        self.assertEqual(xiaConfig.xsr_api_endpoint,
                         xsr_api_endpoint)
        self.assertEqual(xiaConfig.token_url,
                         token_url)
        self.assertEqual(xiaConfig.edx_client_id,
                         edx_client_id)
        self.assertEqual(xiaConfig.edx_client_secret,
                         edx_client_secret)

    def test_create_two_xsr_configuration(self):
        """Test that trying to create more than one XSR Configuration throws
        ValidationError """
        with self.assertRaises(ValidationError):
            xsrConfig = \
                XSRConfiguration(xsr_api_endpoint="xsr_api_endpoint",
                                 token_url="token_url",
                                 edx_client_id="edx_client_id",
                                 edx_client_secret="edx_client_secret")
            xsrConfig2 = \
                XSRConfiguration(xsr_api_endpoint="xsr_api_endpoint2",
                                 token_url="token_url2",
                                 edx_client_id="edx_client_id2",
                                 edx_client_secret="edx_client_secret2")

            xsrConfig.save()
            xsrConfig2.save()
