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
    logger.debug("Sending source data in dataframe format for EVTVL")
    return std_source_df
