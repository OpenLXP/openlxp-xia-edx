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
        self.key_value_hash = "4c8861e7efb81630d6f1c3aa76cc757c03c3" \
                              "31e17aff8cb3ec6211c7f97760ddc3d6a5ea459" \
                              "a72ac8f4e07774f572b5344bed121b6ca7f58c38b885" \
                              "dc0adc138"
        self.hash_value = "9611b484a2165644bd9101691a9b0226d357a35a01" \
                          "2125612e477b9ea61e07ffcd942b538756eef4dbc71b05" \
                          "6ff35545456e195e30f5af6892c698e50ecf5417"

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
