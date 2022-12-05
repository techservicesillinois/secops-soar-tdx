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
URL = "https://help.uillinois.edu"
ACCOUNT_NAME = "None/Not Found"  # TODO: Pull from config as part of issue #13

# To record, `export VCRMODE=once`
VCRMODE = os.environ.get('VCRMODE', 'none'), 


class CleanYAMLSerializer:
    def serialize(cassette: dict):
        for interaction in cassette['interactions']:
            clean_token(interaction)
            clean_search(interaction)
            clean_new_ticket(interaction)
            clean_people_lookup(interaction)
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
        if item['Name'] == ACCOUNT_NAME:
            result = item
    body = [result]

    interaction['response']['body']['string'] = json.dumps(body)


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
    body['RequestorEmail'] = 'nobody@example.com'
    body['RequestorName'] = 'Jane Doe'
    body['RequestorFirstName'] = 'Jane'
    body['RequestorLastName'] = 'Doe'
    body['RequestorPhone'] = None

    body['Notify'][0]['Name'] = 'Jane Doe'
    body['Notify'][0]['Value'] = 'nobody@example.com'
    interaction['response']['body']['string'] = json.dumps(body)

def clean_people_lookup(interaction: dict):
    uri = f"{URL}/SBTDWebApi/api/people/lookup?searchText=buch1&maxResults=1"

    if interaction['request']['uri'] != uri:
        return

    body = json.loads(interaction['response']['body']['string'])
    # body['Uri'] = body['Uri'].replace(str(body['ID']), str(id))

    body[0]['FirstName'] = 'Jane'
    body[0]['LastName'] = 'Doe'
    body[0]['MiddleName'] = None
    body[0]['FullName'] = 'Jane Doe'

    body[0]['HomePhone'] = None
    body[0]['PrimaryPhone'] = None
    body[0]['WorkPhone'] = None
    body[0]['OtherPhone'] = None
    body[0]['MobilePhone'] = None

    body[0]['PrimaryEmail'] = 'nobody@example.com'
    body[0]['AlternateEmail'] = 'nobody@example.com'
    body[0]['AlertEmail'] = 'nobody@example.com'

    interaction['response']['body']['string'] = json.dumps(body)


@pytest.fixture
def connector(monkeypatch) -> TdxConnector:
    conn = TdxConnector()
    if VCRMODE == 'none':  # Always use cassette values when using cassette
        conn.config = {
            "TDX_USERNAME": CASSETTE_USERNAME,
            "TDX_PASSWORD": CASSETTE_PASSWORD,
        }
    else:  # User environment values
        username = os.environ.get('TDX_USERNAME', None)
        if not username:
            raise ValueError('TDX_USERNAME unset or empty with record mode')

        password = os.environ.get('TDX_PASSWORD', None)
        if not password:
            raise ValueError('TDX_PASSWORD unset or empty with record mode')

        conn.config = {
            "TDX_USERNAME": username,
            "TDX_PASSWORD": password,
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


@pytest.fixture
def cassette(request) -> vcr.cassette.Cassette:
    my_vcr = vcr.VCR(
        cassette_library_dir='cassettes',
        record_mode=VCRMODE,
        before_record_request=remove_creds,
        filter_headers=[('Authorization', 'Bearer FAKE_TOKEN')],
        match_on=['uri', 'method'],
    )
    my_vcr.register_serializer("cleanyaml", CleanYAMLSerializer)

    with my_vcr.use_cassette(f'{request.function.__name__}.yaml',
                             serializer="cleanyaml") as tape:
        yield tape
        if my_vcr.record_mode == 'none':  # Tests only valid when not recording
            assert tape.all_played, \
                f"Only played back {len(tape.responses)} responses"
