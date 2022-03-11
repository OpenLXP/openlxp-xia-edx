import hashlib
import json
import logging

import pandas as pd
import requests
from openlxp_xia.management.utils.xia_internal import get_key_dict

from core.models import XSRConfiguration

logger = logging.getLogger('dict_config_logger')


def get_xsr_api_endpoint():
    """Retrieve xis_api_endpoint from XSR configuration """
    logger.debug("Retrieve xsr_api_endpoint from XIS configuration")
    xsr_data = XSRConfiguration.objects.first()
    xsr_api_endpoint = xsr_data.xsr_api_endpoint
    return xsr_api_endpoint


def token_generation_for_api_endpoint():
    """Function connects to edX domain using client id and secret and returns
    the access token"""
    xsr_data = XSRConfiguration.objects.first()

    payload = "grant_type=client_credentials&client_id=" \
              + xsr_data.edx_client_id + "&client_secret=" \
              + xsr_data.edx_client_secret + "&token_type=JWT"
    headers = {'content-type': "application/x-www-form-urlencoded"}
    xis_response = requests.post(url=xsr_data.token_url,
                                 data=payload, headers=headers)

    data = xis_response.json()
    return data['access_token']


def get_xsr_api_response(url):
    """Function to get api response from xsr endpoint"""

    # creating HTTP response object from given url
    headers = {'Authorization': 'JWT ' + token_generation_for_api_endpoint()}
    resp = requests.get(url, headers=headers, )
    return resp


def extract_source():
    """Function to connect to edX endpoint API and get source metadata"""

    logger.info("Retrieving data from source")
    source_df_list = []
    url = get_xsr_api_endpoint()
    resp = get_xsr_api_response(url)
    source_data_dict = json.loads(resp.text)

    while True:
        source_df = pd.DataFrame(source_data_dict['results'])
        source_df_list.append(source_df)
        if not source_data_dict['next']:
            source_df_final = pd.concat(source_df_list).reset_index(drop=True)
            logger.debug("Completed retrieving data from source")
            # return source_data_dict['results']
            return source_df_final
        else:
            resp = get_xsr_api_response(source_data_dict['next'])
            source_data_dict = json.loads(resp.text)


def read_source_file():
    """Sending source data in dataframe format"""
    logger.info("Retrieving data from XSR")

    # Function call to extract data from source repository
    source_df = extract_source()

    # Changing null values to None for source dataframe
    std_source_df = source_df.where(pd.notnull(source_df),
                                    None)
    #  Creating list of dataframes of sources
    source_list = [std_source_df]

    logger.debug("Sending source data in dataframe format for EVTVL")
    return source_list


def get_source_metadata_key_value(data_dict):
    """Function to create key value for source metadata """
    # field names depend on source data and SOURCESYSTEM is system generated
    field = ['key', 'SOURCESYSTEM']
    field_values = []

    for item in field:
        if not data_dict.get(item):
            logger.info('Field name ' + item + ' is missing for '
                                               'key creation')
        field_values.append(data_dict.get(item))

    # Key value creation for source metadata
    key_value = '_'.join(field_values)

    # Key value hash creation for source metadata
    key_value_hash = hashlib.sha512(key_value.encode('utf-8')).hexdigest()

    # Key dictionary creation for source metadata
    key = get_key_dict(key_value, key_value_hash)

    return key
