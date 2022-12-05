import re
from typing import Union
import datetime
import gzip
import json
import jwt
import logging
import os

import pytest
import vcr

from phTDX.tdx_connector import TdxConnector
from vcr.serializers import yamlserializer

# Required pytest plugins
pytest_plugins = ("splunk-soar-connectors")

CASSETTE_USERNAME = "FAKE_USERNAME"
CASSETTE_PASSWORD = "FAKE_PASSWORD"
# Use 'once' in development, 'none' when done
URL = "https://help.uillinois.edu"
VCRMODE = os.environ.get('VCRMODE', 'none'),


class CleanYAMLSerializer:
    def serialize(cassette: dict):
        # import ipdb; ipdb.set_trace()
        # cassette['interactions'][0].keys()
        # dict_keys(['request', 'response'])
        # cassette['interactions'][0]['request']['uri']
        # cassette['interactions'][0]['response']['body']
        for interaction in cassette['interactions']:
            clean_token(interaction)
            clean_search(interaction)
            clean_new_ticket(interaction)
        return yamlserializer.serialize(cassette)

    def deserialize(cassette: str):
        return yamlserializer.deserialize(cassette)


def clean_token(interaction: dict):
    uri = f"{URL}/SBTDWebApi/api/auth"
    if interaction['request']['uri'] != uri:
        return

    token = jwt.encode(
        {'exp': datetime.datetime(2049, 6, 25)},
        'arenofun', algorithm='HS256')
    response = interaction['response']
    if 'Content-Encoding' in response['headers'].keys() and \
        response['headers']['Content-Encoding'] == ['gzip']:
        token = gzip.compress(bytes(token, "ascii"))
    response['body']['string'] = token


def clean_search(interaction: dict):
    uri = f"{URL}/SBTDWebApi/api/accounts/search"
    if interaction['request']['uri'] != uri:
        return
    
    body = json.loads(interaction['response']['body']['string'])
    result = {}
    for item in body:
        if item['Name'] == "None/Not Found":  # TODO: Pull from config?
            result = item
    body = [result]

    interaction['response']['body']['string'] = json.dumps(body)
    # 5125:5250
    # 5125:5167 - PASS 
    # 5125:5156 - PASS 
    # 5125:5140 - PASS 
    # 5132:5140 - PASS 
    # 5136:5140 - PASS 
    # 5136:5138 - PASS 
    # 5137 - PASS
    # with open("debug.txt", "w") as f:
    #     f.write(f"Length: {len(body)}")
    # Length: 8134


def clean_new_ticket(interaction: dict):
    id = 564073
    uri = f"{URL}/SBTDWebApi/api/66/tickets/?EnableNotifyReviewer=False" + \
        "&NotifyRequestor=False&NotifyResponsible=False" + \
        "&AllowRequestorCreation=False"
    
    if interaction['request']['uri'] != uri:
        return
    
    body = json.loads(interaction['response']['body']['string'])
    body['Uri'] = body['Uri'].replace(str(body['ID']), str(id))
    body['ID'] = id
    interaction['response']['body']['string'] = json.dumps(body)


@pytest.fixture
def connector(monkeypatch) -> TdxConnector:
    # TODO: Add warning (or raise an Error) when
    # credentials are not present and a cassette is also not present.
    conn = TdxConnector()
    conn.config = {
        "TDX_USERNAME": os.environ.get('TDX_USERNAME', CASSETTE_USERNAME),
        "TDX_PASSWORD": os.environ.get('TDX_PASSWORD', CASSETTE_PASSWORD),
    }
    if VCRMODE == 'none':  # Always use cassette values when using cassette
        conn.config = {
            "TDX_USERNAME": CASSETTE_USERNAME,
            "TDX_PASSWORD": CASSETTE_PASSWORD,
        }
    conn.logger.setLevel(logging.INFO)
    return conn


def remove_creds(request):
    if not request.body:
        return request
    data = json.loads(request.body.decode('utf-8'))

    if 'password' in data:
        data['password'] = CASSETTE_PASSWORD
    if 'username' in data:
        data['username'] = CASSETTE_USERNAME

    request.body = json.dumps(data)
    return request


def json_sanitize(value: Union[str, dict, list], is_value=True) -> Union[str, dict, list]:
    """
    Modified version of https://stackoverflow.com/a/45526935/2635443

    Recursive function that allows to remove any special characters from json, especially unknown control characters
    """
    if isinstance(value, dict):
        # TODO: Add check that 'string' is in bytes
        if 'string' in value:
            # import pdb; pdb.set_trace()
            result = json_sanitize(json.loads(value['string'].decode()))
            value['string'] = bytes(result, 'ascii')
            return value

        # TODO: Lots more keys
        clean_keys = ['Phone', 'PrimaryEmail']

        # for key in clean_keys:
        # import pdb; pdb.set_trace()
        if 'PrimaryEmail' in value:
            value[key] = 'CLEANED'

        value = {json_sanitize(k, False): json_sanitize(v, True)
                 for k, v in value.items()}
    elif isinstance(value, list):
        value = [json_sanitize(v, True) for v in value]
    elif isinstance(value, str):
        pass
    return value


def clean_json_string(json_string):
    import re
    finder = re.compile('"PrimaryEmail":.*,')
    clean_string = re.sub(finder, '"PrimaryEmail": "CLEANED",', json_string)
    return clean_string


def remove_token(response):
    # if not "body" in response:
    #     return response
    # import pdb; pdb.set_trace()

    # response['body'] = json_sanitize(response['body'])
    # response['body']['string'] = bytes(clean_json_string(str(response['body']['string'])), 'ascii')

    return response


@pytest.fixture
def cassette(request) -> vcr.cassette.Cassette:
    my_vcr = vcr.VCR(
        cassette_library_dir='cassettes',
        record_mode=VCRMODE,
        before_record_request=remove_creds,
        before_record_response=remove_token,
        filter_headers=[('Authorization', 'Bearer FAKE_TOKEN')],
        match_on=['uri', 'method'],
    )
    my_vcr.allow_playback_repeats = True  # Required due to double Auth()
    my_vcr.register_serializer("cleanyaml", CleanYAMLSerializer)

    with my_vcr.use_cassette(f'{request.function.__name__}.yaml',
                             serializer="cleanyaml") as tape:
        yield tape
        if my_vcr.record_mode == 'none':  # Tests only valid when not recording
            assert tape.all_played, \
                f"Only played back {len(tape.responses)} responses"
