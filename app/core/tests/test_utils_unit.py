import hashlib
import logging
from unittest.mock import patch

import pandas as pd
from ddt import data, ddt, unpack
from django.test import tag

from core.management.utils.xia_internal import (dict_flatten,
                                                flatten_dict_object,
                                                flatten_list_object,
                                                get_key_dict,
                                                get_publisher_detail,
                                                get_source_metadata_key_value,
                                                get_target_metadata_key_value,
                                                replace_field_on_target_schema,
                                                update_flattened_object)
from core.management.utils.xis_client import get_xis_api_endpoint
from core.management.utils.xsr_client import (get_xsr_api_endpoint,
                                              get_xsr_api_response,
                                              read_source_file)
from core.management.utils.xss_client import (
    get_aws_bucket_name, get_required_fields_for_validation,
    get_source_validation_schema, get_target_metadata_for_transformation,
    get_target_validation_schema)
from core.models import XIAConfiguration

from .test_setup import TestSetUp

logger = logging.getLogger('dict_config_logger')


@tag('unit')
@ddt
class UtilsTests(TestSetUp):
    """Unit Test cases for utils """

    # Test cases for XIA_INTERNAL

    def test_get_publisher_detail(self):
        """Test to retrieve publisher from XIA configuration"""
        with patch('core.management.utils.xia_internal'
                   '.XIAConfiguration.objects') as xdsCfg:
            xiaConfig = XIAConfiguration(publisher='edX')
            xdsCfg.first.return_value = xiaConfig
            return_from_function = get_publisher_detail()
            self.assertEqual(xiaConfig.publisher, return_from_function)

    @data(('test_key', 'test_key_hash'), ('test_key1', 'test_key_hash2'))
    @unpack
    def test_get_key_dict(self, first_value, second_value):
        """Test for key dictionary creation"""
        expected_result = {
            'key_value': first_value,
            'key_value_hash': second_value
        }
        result = get_key_dict(first_value, second_value)
        self.assertEquals(result, expected_result)

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

    def test_replace_field_on_target_schema(self):
        """test to check if values under educational context are replaced"""
        test_dict0 = {'0': {
            "Course": {
                "EducationalContext": "Y"
            }
        }
        }

        test_dict1 = {'1': {
            "Course": {
                "EducationalContext": "n"
            }
        }
        }

        replace_field_on_target_schema('0', test_dict0)
        self.assertEqual(test_dict0['0']['Course']['EducationalContext'],
                         'Mandatory')

        replace_field_on_target_schema('1', test_dict1)
        self.assertEqual(test_dict1['1']['Course']['EducationalContext'],
                         'Non - Mandatory')

    @data(('key_field1', 'key_field2'), ('key_field11', 'key_field22'))
    @unpack
    def test_get_target_metadata_key_value(self, first_value, second_value):
        """Test key dictionary creation for target"""

        test_dict = {'Course': {
            'CourseCode': first_value,
            'CourseProviderName': second_value
        }}

        expected_key = first_value + '_' + second_value
        expected_key_hash = hashlib.md5(expected_key.encode('utf-8')). \
            hexdigest()

        result_key_dict = get_target_metadata_key_value(test_dict)
        self.assertEqual(result_key_dict['key_value'], expected_key)
        self.assertEqual(result_key_dict['key_value_hash'], expected_key_hash)

    def test_dict_flatten(self):
        """Test function to navigate to value in source
        metadata to be validated"""
        test_data_dict = {"key1": "value1",
                          "key2": {"sub_key1": "sub_value1"},
                          "key3": [{"sub_key2": "sub_value2"},
                                   {"sub_key3": "sub_value3"}]}

        with patch('core.management.utils.xia_internal.flatten_list_object') \
                as mock_flatten_list, \
                patch('core.management.utils.xia_internal.flatten_dict_'
                      'object') as mock_flatten_dict, \
                patch('core.management.utils.xia_internal.update_flattened_'
                      'object') as mock_update_flattened:
            mock_flatten_list.return_value = mock_flatten_list
            mock_flatten_list.return_value = None
            mock_flatten_dict.return_value = mock_flatten_dict
            mock_flatten_dict.return_value = None
            mock_update_flattened.return_value = mock_update_flattened
            mock_update_flattened.return_value = None

        return_value = dict_flatten(test_data_dict,
                                    self.test_required_column_names)
        self.assertTrue(return_value)

    @data(
        ([{'a.b': None, 'a.c': 'value2', 'd': None},
          {'a.b': 'value1', 'a.c': 'value2', 'd': None}]))
    def test_flatten_list_object_loop(self, value):
        """Test the looping od the function to flatten
        list object when the value is list"""
        prefix = 'a'
        flatten_dict = {}
        required_list = ['a.b', 'a.c', 'd']
        with patch('core.management.utils.xia_internal.flatten_list_object') \
                as mock_flatten_list, \
                patch('core.management.utils.xia_internal.flatten_dict_'
                      'object') as mock_flatten_dict, \
                patch('core.management.utils.xia_internal.update_flattened_'
                      'object') as mock_update_flattened:
            mock_flatten_list.return_value = mock_flatten_list
            mock_flatten_list.return_value = None
            mock_flatten_dict.return_value = mock_flatten_dict
            mock_flatten_dict.return_value = None
            mock_update_flattened.side_effect = flatten_dict = \
                {'a.b': None, 'a.c': 'value2'}

            flatten_list_object(value, prefix, flatten_dict, required_list)
            self.assertEqual(mock_flatten_dict.call_count, 2)

    @data(
        ([{'b': [None]}]))
    def test_flatten_list_object_multilevel(self, value):
        """Test the function to flatten list object
         when the value is list for multilevel lists"""
        prefix = 'a'
        flatten_dict = {}
        required_list = ['a.b', 'd']
        with patch('core.management.utils.xia_internal.flatten_list_object') \
                as mock_flatten_list, \
                patch('core.management.utils.xia_internal.flatten_dict_'
                      'object') as mock_flatten_dict, \
                patch('core.management.utils.xia_internal.update_flattened_'
                      'object') as mock_update_flattened:
            mock_flatten_list.return_value = mock_update_flattened
            mock_flatten_dict.return_value = mock_flatten_list()
            mock_update_flattened.side_effect = flatten_dict = \
                {'a.b': None}

            flatten_list_object(value, prefix, flatten_dict, required_list)
            self.assertEqual(mock_flatten_list.call_count, 1)

    @data(([{'A': 'a'}]), ([{'B': 'b', 'C': 'c'}]))
    def test_flatten_list_object_list(self, value):
        """Test the function to flatten list object when the value is list"""
        prefix = 'test'
        flatten_dict = []
        with patch('core.management.utils.xia_internal.flatten_list_object') \
                as mock_flatten_list, \
                patch('core.management.utils.xia_internal.flatten_dict_'
                      'object') as mock_flatten_dict, \
                patch('core.management.utils.xia_internal.update_flattened_'
                      'object') as mock_update_flattened:
            mock_flatten_list.return_value = mock_flatten_list
            mock_flatten_list.return_value = None
            mock_flatten_dict.return_value = mock_flatten_dict
            mock_flatten_dict.return_value = None
            mock_update_flattened.return_value = mock_update_flattened
            mock_update_flattened.return_value = None

            flatten_list_object(value, prefix, flatten_dict,
                                self.test_required_column_names)

            self.assertEqual(mock_flatten_dict.call_count, 1)

    @data(([{'A': 'a'}]), ([{'B': 'b', 'C': 'c'}]))
    def test_flatten_list_object_dict(self, value):
        """Test the function to flatten list object when the value is dict"""
        prefix = 'test'
        flatten_dict = []
        with patch('core.management.utils.xia_internal.flatten_list_object') \
                as mock_flatten_list, \
                patch('core.management.utils.xia_internal.flatten_dict_'
                      'object') as mock_flatten_dict, \
                patch('core.management.utils.xia_internal.update_flattened_'
                      'object') as mock_update_flattened:
            mock_flatten_list.return_value = mock_flatten_list
            mock_flatten_list.return_value = None
            mock_flatten_dict.return_value = mock_flatten_dict
            mock_flatten_dict.return_value = None
            mock_update_flattened.return_value = mock_update_flattened
            mock_update_flattened.return_value = None

            flatten_list_object(value, prefix, flatten_dict,
                                self.test_required_column_names)

            self.assertEqual(mock_flatten_dict.call_count, 1)

    @data((['hello']), (['hi']))
    def test_flatten_list_object_str(self, value):
        """Test the function to flatten list object when the value is string"""
        prefix = 'test'
        flatten_dict = []
        with patch('core.management.utils.xia_internal.flatten_list_object') \
                as mock_flatten_list, \
                patch('core.management.utils.xia_internal.flatten_dict_'
                      'object') as mock_flatten_dict, \
                patch('core.management.utils.xia_internal.update_flattened_'
                      'object') as mock_update_flattened:
            mock_flatten_list.return_value = mock_flatten_list
            mock_flatten_list.return_value = None
            mock_flatten_dict.return_value = mock_flatten_dict
            mock_flatten_dict.return_value = None
            mock_update_flattened.return_value = mock_update_flattened
            mock_update_flattened.return_value = None
            flatten_list_object(value, prefix, flatten_dict,
                                self.test_required_column_names)

            self.assertEqual(mock_update_flattened.call_count, 1)

    @data(({'abc': {'A': 'a'}}), ({'xyz': {'B': 'b'}}))
    def test_flatten_dict_object_dict(self, value):
        """Test the function to flatten dictionary object when input value is
        a dict"""
        prefix = 'test'
        flatten_dict = []
        with patch('core.management.utils.xia_internal.flatten_list_object') \
                as mock_flatten_list, \
                patch('core.management.utils.xia_internal.flatten_dict_'
                      'object') as mock_flatten_dict, \
                patch('core.management.utils.xia_internal.update_flattened_'
                      'object') as mock_update_flattened:
            mock_flatten_list.return_value = mock_flatten_list
            mock_flatten_list.return_value = None
            mock_flatten_dict.return_value = mock_flatten_dict
            mock_flatten_dict.return_value = None
            mock_update_flattened.return_value = mock_update_flattened
            mock_update_flattened.return_value = None

            flatten_dict_object(value, prefix, flatten_dict,
                                self.test_required_column_names)

            self.assertEqual(mock_flatten_dict.call_count, 1)

    @data(({'abc': [1, 2, 3]}), ({'xyz': [1, 2, 3, 4, 5]}))
    def test_flatten_dict_object_list(self, value):
        """Test the function to flatten dictionary object when input value is
        a list"""
        prefix = 'test'
        flatten_dict = []
        with patch('core.management.utils.xia_internal.flatten_list_object') \
                as mock_flatten_list, \
                patch('core.management.utils.xia_internal.flatten_dict_'
                      'object') as mock_flatten_dict, \
                patch('core.management.utils.xia_internal.update_flattened_'
                      'object') as mock_update_flattened:
            mock_flatten_list.return_value = mock_flatten_list
            mock_flatten_list.return_value = None
            mock_flatten_dict.return_value = mock_flatten_dict
            mock_flatten_dict.return_value = None
            mock_update_flattened.return_value = mock_update_flattened
            mock_update_flattened.return_value = None

            flatten_dict_object(value, prefix, flatten_dict,
                                self.test_required_column_names)

            self.assertEqual(mock_flatten_list.call_count, 1)

    @data(({'abc': 'A'}), ({'xyz': 'B'}))
    def test_flatten_dict_object_str(self, value):
        """Test the function to flatten dictionary object when input value is
        a string"""
        prefix = 'test'
        flatten_dict = []
        with patch('core.management.utils.xia_internal.flatten_list_object') \
                as mock_flatten_list, \
                patch('core.management.utils.xia_internal.flatten_dict_'
                      'object') as mock_flatten_dict, \
                patch('core.management.utils.xia_internal.update_flattened_'
                      'object') as mock_update_flattened:
            mock_flatten_list.return_value = mock_flatten_list
            mock_flatten_list.return_value = None
            mock_flatten_dict.return_value = mock_flatten_dict
            mock_flatten_dict.return_value = None
            mock_update_flattened.return_value = mock_update_flattened
            mock_update_flattened.return_value = None

            flatten_dict_object(value, prefix, flatten_dict,
                                self.test_required_column_names)

            self.assertEqual(mock_update_flattened.call_count, 1)

    @data('', 'str1')
    def test_update_flattened_object(self, value):
        """Test the function which returns the source bucket name"""
        prefix = 'test'
        flatten_dict = {}
        update_flattened_object(value, prefix, flatten_dict)
        self.assertTrue(flatten_dict)

    # Test cases for XIS_CLIENT

    def test_get_api_endpoint(self):
        """Test to check if API endpoint is present"""
        result_api_value = get_xis_api_endpoint()
        logger.info(result_api_value)
        self.assertTrue(result_api_value)

    # Test cases for XSR_CLIENT

    def test_get_xsr_endpoint(self):
        """Test to check if XSR endpoint is present"""
        result_xsr_endpoint = get_xsr_api_endpoint()
        self.assertTrue(result_xsr_endpoint)

    def test_get_xsr_api_response(self):
        """Test to Function to get api response from xsr endpoint"""
        result_xsr_api_response = get_xsr_api_response()
        self.assertTrue(result_xsr_api_response)

    @patch('core.management.utils.xsr_client.extract_source',
           return_value=dict({1: {'a': 'b'}}))
    def test_read_source_file(self, extract):
        """test to check if data is present for extraction """

        result_data = read_source_file()
        self.assertIsInstance(result_data, pd.DataFrame)

    # Test cases for XSS_CLIENT

    def test_get_aws_bucket_name(self):
        """Test the function which returns the source bucket name"""
        result_bucket = get_aws_bucket_name()
        self.assertTrue(result_bucket)

    def test_get_source_validation_schema(self):
        """Test to retrieve source_metadata_schema from XIA configuration"""
        with patch('core.management.utils.xss_client'
                   '.XIAConfiguration.objects') as xdsCfg, \
                patch('core.management.utils.xss_client'
                      '.read_json_data') as read_obj:
            xiaConfig = XIAConfiguration(
                source_metadata_schema='edX_source_validate_schema.json')
            xdsCfg.return_value = xiaConfig
            read_obj.return_value = read_obj
            read_obj.return_value = self.schema_data_dict
            return_from_function = get_source_validation_schema()
            self.assertEqual(read_obj.return_value,
                             return_from_function)

    def test_get_required_fields_for_validation(self):
        """Test for Creating list of fields which are Required """

        required_column_name, recommended_column_name = \
            get_required_fields_for_validation(self.schema_data_dict)

        self.assertTrue(required_column_name)
        self.assertTrue(recommended_column_name)

    def test_get_target_validation_schema(self):
        """Test to retrieve target_metadata_schema from XIA configuration"""
        with patch('core.management.utils.xss_client'
                   '.XIAConfiguration.objects') as xiaconfigobj, \
                patch('core.management.utils.xss_client'
                      '.read_json_data') as read_obj:
            xiaConfig = XIAConfiguration(
                target_metadata_schema='p2881_target_validation_schema.json')
            xiaconfigobj.return_value = xiaConfig
            read_obj.return_value = read_obj
            read_obj.return_value = self.schema_data_dict
            return_from_function = get_target_validation_schema()
            self.assertEqual(read_obj.return_value,
                             return_from_function)

    def test_get_target_metadata_for_transformation(self):
        """Test to retrieve target metadata schema from XIA configuration """
        with patch('core.management.utils.xss_client'
                   '.XIAConfiguration.objects') as xia_config_obj, \
                patch('core.management.utils.xss_client'
                      '.read_json_data') as read_obj:
            xiaConfig = XIAConfiguration(
                source_target_mapping='edX_p2881_target_metadata_schema.json')
            xia_config_obj.return_value = xiaConfig
            read_obj.return_value = read_obj
            read_obj.return_value = self.target_data_dict
            return_from_function = get_target_metadata_for_transformation()
            self.assertEqual(read_obj.return_value,
                             return_from_function)