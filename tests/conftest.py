import json
import logging
import os
import pathlib

import pytest
import vcr

from phTDX.tdx_connector import TdxConnector

# Required pytest plugins
pytest_plugins = ("splunk-soar-connectors")


@pytest.fixture
def connector(monkeypatch) -> TdxConnector:
    # TODO: Add warning (or raise an Error) when
    # credentials are not present and a cassette is also not present.
    conn = TdxConnector()
    conn.config = {
        "TDX_USERNAME": os.environ.get('TDX_USERNAME', "FAKE_USERNAME"),
        "TDX_PASSWORD": os.environ.get('TDX_PASSWORD', "fakepassword"),
    }
    conn.logger.setLevel(logging.INFO)
    return conn


def remove_creds(request):
    if not request.body:
        return request
    data = json.loads(request.body.decode('utf-8'))

    if 'password' in data:
        data['password'] = 'FAKE'
    if 'username' in data:
        data['username'] = 'FOOBAR'

    request.body = json.dumps(data)
    return request


def remove_token(response):
    if not "body" in response:
        return response
    # TODO: Strip newlines from our expired token.
    if "'string': b'" in str(response["body"]):
        with open('./cassettes/expired_token.txt', 'r') as f:
            # import ipdb; ipdb.set_trace()
            response["body"]["string"] = \
                str.encode("".join(f.read().splitlines()))

    return response


@pytest.fixture
def cassette(request) -> vcr.cassette.Cassette:
    my_vcr = vcr.VCR(
        cassette_library_dir='cassettes',
        record_mode='once',  # Use 'once' in development, 'none' when done
        before_record_request=remove_creds,
        before_record_response=remove_token,
        filter_headers=[('Authorization', 'Bearer FAKE_TOKEN')],
        match_on=['uri', 'method'],
    )

    with my_vcr.use_cassette(f'{request.function.__name__}.yaml') as tape:
        yield tape
        assert tape.all_played, f"Only played back {len(tape.responses)} responses"
