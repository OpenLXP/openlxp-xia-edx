import json
import logging
import os

import pandas as pd
import requests

logger = logging.getLogger('dict_config_logger')


def get_xsr_api_endpoint():
    """Setting API endpoint from XIA and XIS communication """
    xsr_endpoint = os.environ.get('XSR_API_ENDPOINT')
    return xsr_endpoint


def token_generation_for_api_endpoint():
    """Function connects to edX domain using client id and secret and returns
    the access token"""

    payload = "grant_type=client_credentials&client_id=" + os.environ.get(
        'EDX_CLIENT_ID') + "&client_secret=" + os.environ.get(
        'EDX_CLIENT_SECRET') + "&token_type=JWT"
    headers = {'content-type': "application/x-www-form-urlencoded"}
    xis_response = requests.post(url=os.environ.get('TOKEN_URL'),
                                 data=payload, headers=headers)
    data = xis_response.json()
    return data['access_token']


def get_xsr_api_response():
    """Function to get api response from xsr endpoint"""
    url = get_xsr_api_endpoint()
    # creating HTTP response object from given url
    headers = {'Authorization': 'JWT '+token_generation_for_api_endpoint()}
    resp = requests.get(url, headers=headers, )
    return resp


def extract_source():
    """function to connect to edX endpoint API and get source metadata"""

    resp = get_xsr_api_response()
    source_data_dict = json.loads(resp.text)

    return source_data_dict['results']


def read_source_file():
    """sending source data in dataframe format"""
    logger.info("Retrieving data from XSR")
    # load rss from web to convert to xml
    xsr_items = extract_source()
    # convert xsr dictionary list to Dataframe
    source_df = pd.DataFrame(xsr_items)
    logger.info("Changing null values to None for source dataframe")
    std_source_df = source_df.where(pd.notnull(source_df),
                                    None)
    return std_source_df
