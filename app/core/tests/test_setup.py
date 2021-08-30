import pandas as pd
from django.test import TestCase


class TestSetUp(TestCase):
    """Class with setup and teardown for tests in XIS"""

    def setUp(self):
        """Function to set up necessary data for testing"""

        # globally accessible data sets

        self.source_metadata = {
            "Test": "0",
            "Test_id": "2146",
            "Test_url": "https://example.test.com/",
            "End_date": "9999-12-31T00:00:00-05:00",
            "test_name": "test name",
            "Start_date": "2017-03-28T00:00:00-04:00",
            "LearningResourceIdentifier": "TestData 123",
            "key": "TestData 123",
            "SOURCESYSTEM": "edX",
            "test_description": "test description",
        }

        self.key_value = "TestData 123_edX"
        self.key_value_hash = "f1f0c8c3b622b58eddd8d6fa8555d994"
        self.hash_value = "07d12a959d362659fd14ed7bdbed5024"

        self.test_data = {
            "key1": ["val1"],
            "key2": ["val2"],
            "key3": ["val3"]}
        self.token_url = 'https://api.edx.org/oauth2/v1/access_token'

        self.xsr_api_endpoint_url = \
            'https://api.edx.org/catalog/v1/catalogs/820/courses/'

        self.metadata_df = pd.DataFrame.from_dict({1: self.source_metadata},
                                                  orient='index')

        return super().setUp()

    def tearDown(self):
        return super().tearDown()
