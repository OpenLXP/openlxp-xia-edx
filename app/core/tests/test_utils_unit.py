import hashlib
import logging
from unittest.mock import patch

import numpy as np
import pandas as pd
from ddt import data, ddt, unpack
from django.test import tag

from core.management.utils.xsr_client import (
    extract_source, get_source_metadata_key_value, get_xsr_api_endpoint,
    get_xsr_api_response, read_source_file, token_generation_for_api_endpoint)
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
        expected_key_hash = hashlib.sha512(expected_key.encode('utf-8')). \
            hexdigest()

        result_key_dict = get_source_metadata_key_value(test_dict)
        self.assertEqual(result_key_dict['key_value'], expected_key)
        self.assertEqual(result_key_dict['key_value_hash'], expected_key_hash)

    @data(('key_field1', ''))
    @unpack
    def test_get_source_metadata_key_value_fail(self,
                                                first_value, second_value):
        """Test key dictionary creation for source"""
        test_dict = {
            'key': first_value,
            'SOURCESYSTEM': second_value
        }

        result_key_dict = get_source_metadata_key_value(test_dict)

        self.assertEqual(result_key_dict, None)

    # Test cases for XSR_CLIENT unique to edX

    def test_token_generation_for_api_endpoint(self):
        """Test Function connects to edX domain using
        client id and secret and returns the access token"""

        with patch('core.management.utils.xsr_client'
                   '.requests') as mock_req:
            mock_req.post.return_value.json.return_value = {'access_token': 1}
            xsr_data = XSRConfiguration(xsr_api_endpoint="xsr_api_endpoint",
                                        token_url="token_url",
                                        edx_client_id="edx_client_id",
                                        edx_client_secret="edx_client_secret")
            xsr_data.save()
            response = token_generation_for_api_endpoint()

            self.assertEqual(response, 1)

    def test_extract_source(self):
        """Test Function to connect to edX endpoint
        API and get source metadata"""

        with patch('core.management.utils.xsr_client.get_xsr_api_endpoint'), \
                patch('core.management.utils.xsr_client.'
                      'get_xsr_api_response') as mock_get_xsr_api_response:
            val = '{"next":"", ' \
                  '"previous":"previous",' \
                  '"results":[{"course":"course", "next":"", ' \
                  '"previous":"previous"}]} '

            mock_get_xsr_api_response.return_value.text = val

            self.assertIsInstance(extract_source(), pd.DataFrame)

    def test_read_source_file(self):
        """Test Sending source data in dataframe format"""
        with patch('core.management.utils.xsr_client.'
                   'extract_source') as mock_extract_source:
            d = {'col1': [1, 2], 'col2': [3, np.nan]}
            df = pd.DataFrame(data=d)

            mock_extract_source.return_value = df

            return_val = read_source_file()
            self.assertIsInstance(return_val, list)

    def test_get_xsr_api_response(self):
        """Test Function to get api response from xsr endpoint"""
        with patch('core.management.utils.xsr_client'
                   '.requests') as mock_req, \
                patch('core.management.'
                      'utils.xsr_client.'
                      'token_generation_for_api_endpoint') as mock_token:
            mock_token.return_value = "token string"
            mock_req.get.return_value = "response"

            self.assertEqual(get_xsr_api_response("url"), "response")
