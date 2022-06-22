import logging
import pathlib
import json

import pytest
import vcr

# from phsoar_null_router.soar_null_router_connector import Soar_Null_RouterConnector

# Required pytest plugins
pytest_plugins = ("splunk-soar-connectors")


# @pytest.fixture
# def connector(monkeypatch) -> Soar_Null_RouterConnector:
#     monkeypatch.setenv("BHR_HOST", "https://nr-test.techservices.illinois.edu")
#     monkeypatch.setenv("BHR_TOKEN", "FAKETOKEN")

#     conn = Soar_Null_RouterConnector()
#     conn.logger.setLevel(logging.INFO)
#     return conn


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


@pytest.fixture
def cassette(request) -> vcr.cassette.Cassette:
    my_vcr = vcr.VCR(
        cassette_library_dir='cassettes',
        record_mode='once',
        before_record_request=remove_creds,
        filter_headers=[('Authorization', 'Bearer FAKE_TOKEN')]
    )

    with my_vcr.use_cassette(f'{request.function.__name__}.yaml') as tape:
        yield tape
