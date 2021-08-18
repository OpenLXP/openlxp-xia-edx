import hashlib
import logging
from unittest.mock import patch
from ddt import data, ddt, unpack
from django.test import tag

from core.management.utils.xsr_client import get_xsr_api_endpoint, \
    get_source_metadata_key_value
from core.models import XSRConfiguration

from .test_setup import TestSetUp

logger = logging.getLogger('dict_config_logger')


@tag('unit')
@ddt
class UtilsTests(TestSetUp):
    """Unit Test cases for utils """

    # Test cases for XSR_CLIENT

    def test_get_xsr_endpoint(self):
        """Test to retrieve xis_api_endpoint from XIS configuration"""
        with patch('core.management.utils.xsr_client'
                   '.XSRConfiguration.objects') as xsrCfg:
            xisConfig = XSRConfiguration(
                xsr_api_endpoint=self.xsr_api_endpoint_url)
            xsrCfg.first.return_value = xisConfig
            return_from_function = get_xsr_api_endpoint()
            self.assertEqual(xisConfig.xsr_api_endpoint, return_from_function)

    @data(('key_field1', 'key_field2'), ('key_field11', 'key_field22'))
    @unpack
    def test_get_source_metadata_key_value(self, first_value, second_value):
        """Test key dictionary creation for source"""
        test_dict = {
            'key': first_value,
            'SOURCESYSTEM': second_value
        }

        expected_key = first_value + '_' + second_value
        expected_key_hash = hashlib.md5(expected_key.encode('utf-8')). \
            hexdigest()

        result_key_dict = get_source_metadata_key_value(test_dict)
        self.assertEqual(result_key_dict['key_value'], expected_key)
        self.assertEqual(result_key_dict['key_value_hash'], expected_key_hash)
