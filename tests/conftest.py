import json
import logging
import os

import pytest
import vcr

from app.app import TdxConnector

from vcr_cleaner import CleanYAMLSerializer, clean_if
from vcr_cleaner.cleaners.jwt_token import clean_token
from vcr_cleaner.cleaners.env_strings import clean_env_strings

# Required pytest plugins
pytest_plugins = ("splunk-soar-connectors")

CASSETTE_USERNAME = "FAKE_USERNAME"
CASSETTE_PASSWORD = "FAKE_PASSWORD"    # pragma: allowlist secret
CASSETTE_NETID = 'thor2'
CASSETTE_ENDPOINT = "help.uillinois.edu"
# TODO: Pull from config as part of issue #13
CASSETTE_ACCOUNT_NAME = "None/Not Found"
CASSETTE_ORG_NAME = CASSETTE_ENDPOINT
CASSETTE_TIMEZONE = "0000"
CASSETTE_LOG_LEVEL = "DEBUG"
APPID = 66  # APPID and URL are also CASSETTE but need short names
URL = f"https://{CASSETTE_ENDPOINT}"

# To record, `export VCR_RECORD=True`
VCR_RECORD = "VCR_RECORD" in os.environ


def clean_search(request: dict, response: dict):
    uri = f"{URL}/SBTDWebApi/api/accounts/search"
    if request['uri'] != uri:
        return

    body = json.loads(response['body']['string'])
    result = {}
    for item in body:
        if item['Name'] == CASSETTE_ACCOUNT_NAME:
            result = item
    body = [result]

    response['body']['string'] = json.dumps(body)


def clean_new_ticket(request: dict, response: dict):
    id = 564073
    uri = f"{URL}/SBTDWebApi/api/{APPID}/tickets/" + \
          "?EnableNotifyReviewer=False" + \
          "&NotifyRequestor=False&NotifyResponsible=False" + \
          "&AllowRequestorCreation=False"

    if request['uri'] != uri:
        return

    body = json.loads(response['body']['string'])
    body['Uri'] = body['Uri'].replace(str(body['ID']), str(id))
    body['ID'] = id
    body['RequestorEmail'] = 'nobody@example.com'
    body['RequestorName'] = 'Jane Foster'
    body['RequestorFirstName'] = 'Jane'
    body['RequestorLastName'] = 'Foster'
    body['RequestorPhone'] = None

    body['Notify'][0]['Name'] = 'Jane Foster'
    body['Notify'][0]['Value'] = 'nobody@example.com'
    response['body']['string'] = json.dumps(body)


def clean_people_lookup(request: dict, response: dict):
    # TODO: Switch the NetID here based on ENV settings and record mode
    netid = os.environ.get('TDX_NETID', CASSETTE_NETID)
    uri = "%s/SBTDWebApi/api/people/lookup?searchText=%s&maxResults=1"

    if request['uri'] != uri % (URL, netid):
        return

    request['uri'] = uri % (URL, 'thor2')
    body = json.loads(response['body']['string'])

    body[0]['Salutation'] = 'Doctor'
    body[0]['FirstName'] = 'Jane'
    body[0]['LastName'] = 'Foster'
    body[0]['MiddleName'] = None
    body[0]['FullName'] = 'Jane Foster'
    body[0]['Nickname'] = 'The Mighty Thor'

    body[0]['HomePhone'] = None
    body[0]['PrimaryPhone'] = None
    body[0]['WorkPhone'] = None
    body[0]['OtherPhone'] = None
    body[0]['MobilePhone'] = None

    body[0]['PrimaryEmail'] = 'nobody@example.com'
    body[0]['AlternateEmail'] = 'nobody@example.com'
    body[0]['AlertEmail'] = 'nobody@example.com'

    response['body']['string'] = json.dumps(body)
    env_netid = os.environ.get('TDX_NETID', None)
    response['body']['string'].replace(env_netid, 'thor2')


@pytest.fixture
def connector(monkeypatch) -> TdxConnector:
    conn = TdxConnector()
    if not VCR_RECORD:  # Always use cassette values when using cassette
        #  TODO: Lots more configs!
        cassette_configs = {
            "username": CASSETTE_USERNAME,
            "password": CASSETTE_PASSWORD,
            "endpoint": CASSETTE_ENDPOINT,
            "appid": APPID,
            "timezone": CASSETTE_TIMEZONE,
            "loglevel": CASSETTE_LOG_LEVEL,
            "sandbox": True,
        }
        os.environ.pop('TDX_NETID', None)
    else:  # User environment values
        env_keys = ['username', 'password', 'netid',
                    'endpoint', 'appid',
                    'timezone', 'loglevel']

        cassette_configs = {}

        for key in env_keys:
            env_key = f"TDX_{key.upper()}"
            cassette_configs[key] = os.environ.get(env_key, None)
            if not cassette_configs[key]:
                raise ValueError(f'{env_key} unset or empty with record mode')

    # Always True - no testing in production.
    conn.config = get_config_defaults(conn)
    conn.config.update(cassette_configs)
    conn.config['sandbox'] = True

    conn.logger.setLevel(logging.INFO)
    return conn


def get_config_defaults(conn):
    conn._load_app_json()

    result = {}
    for key in conn.get_app_config()['configuration'].keys():
        result[key] = conn.get_app_config()['configuration'][key].get(
            'default', '')
    return result


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


@clean_if(uri=f"{URL}/SBTDWebApi/api/auth")
def clean_auth(request, response):
    clean_token(request, response)


@clean_if(uri=f"{URL}/SBTDWebApi/api/groups/search")
def clean_so_many_groups(request, response):
    cleaned_groups = """[{
        "ID": 787,
        "Name": "UIUC-TechServices-Cybersecurity Developers",
        "Description": "",
        "IsActive": true,
        "ExternalID": "",
        "CreatedDate": "2022-11-14T15: 14: 07.957Z",
        "ModifiedDate": "2022-11-14T15: 14: 07.957Z",
        "PlatformApplications": []
    }]"""
    response['body']['string'] = cleaned_groups


@pytest.fixture
def cassette(request) -> vcr.cassette.Cassette:
    my_vcr = vcr.VCR(
        cassette_library_dir='cassettes',
        record_mode='once' if VCR_RECORD else 'none',
        before_record_request=remove_creds,
        filter_headers=[('Authorization', 'Bearer FAKE_TOKEN')],
        match_on=['uri', 'method'],
    )
    yaml_cleaner = CleanYAMLSerializer()
    my_vcr.register_serializer("cleanyaml", yaml_cleaner)
    yaml_cleaner.register_cleaner(clean_auth)
    yaml_cleaner.register_cleaner(clean_search)
    yaml_cleaner.register_cleaner(clean_new_ticket)
    yaml_cleaner.register_cleaner(clean_people_lookup)
    yaml_cleaner.register_cleaner(clean_env_strings)
    yaml_cleaner.register_cleaner(clean_so_many_groups)

    with my_vcr.use_cassette(f'{request.function.__name__}.yaml',
                             serializer="cleanyaml") as tape:
        yield tape
        if my_vcr.record_mode == 'none':  # Tests only valid when not recording
            assert tape.all_played, \
                f"Only played back {len(tape.responses)} responses"
