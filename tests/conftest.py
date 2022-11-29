import json
import logging
import os
import pathlib
import yaml

import pytest
import vcr

from phTDX.tdx_connector import TdxConnector

# Required pytest plugins
pytest_plugins = ("splunk-soar-connectors")

CASSETTE_USERNAME = "FAKE_USERNAME"
CASSETTE_PASSWORD = "FAKE_PASSWORD"
VCRMODE = 'none'  # Use 'once' in development, 'none' when done


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


def remove_token(response):
    if not "body" in response:
        return response
    # import ipdb; ipdb.set_trace()
    if "'string': b'" in str(response["body"]):
        with open('./cassettes/expired_token.txt', 'rb') as f:
            # response['body']['string'] = response['body']['string'].replace(string, replacement)
            # response["body"] = bytes("".join(f.read().splitlines()), "ascii")
            import secrets
            import gzip
            import jwt
            # token = secrets.token_urlsafe(10)
            token = jwt.encode({'exp':'bar'},'secrety', algorithm='HS256')
            response['body']['string'] = gzip.compress(bytes(token, "ascii"))
    return response


@pytest.fixture
def cassette(request) -> vcr.cassette.Cassette:
    my_vcr = vcr.VCR(
        cassette_library_dir='cassettes',
        record_mode=VCRMODE,  # Use 'once' in development, 'none' when done
        before_record_response=remove_token,
        filter_headers=[('Authorization', 'Bearer FAKE_TOKEN')],
        match_on=['uri', 'method'],
    )
    my_vcr.allow_playback_repeats = True # Required due to double Auth()

    with my_vcr.use_cassette(f'{request.function.__name__}.yaml') as tape:
        yield tape
        assert tape.all_played, f"Only played back {len(tape.responses)} responses"
