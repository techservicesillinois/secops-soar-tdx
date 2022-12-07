import json
import os
import sys
from urllib.error import HTTPError

import pytest
import vcr

from unittest.mock import patch, Mock
from requests.exceptions import HTTPError

from phTDX.tdx_connector import TdxConnector

from conftest import VCR_RECORD, CASSETTE_NETID


def test_connectivity(cassette, connector: TdxConnector):
    in_json = {
            "appid": "fceeaac1-8f96-46d6-9c3b-896e363eb004",
            "identifier": "test_connectivity",
            "parameters": [{}], # TODO: Submit an issue asking to allow [] here.
    }

    result = json.loads(connector._handle_action(json.dumps(in_json), None))
    assert result[0]["message"] == "Active connection"


def test_failed_connectivity(cassette, connector: TdxConnector):
    in_json = {
            "appid": "fceeaac1-8f96-46d6-9c3b-896e363eb004",
            "identifier": "test_connectivity",
            "parameters": [{}],
    }

    result = json.loads(connector._handle_action(json.dumps(in_json), None))
    assert result[0]["message"] == "Failed connection"


def test_create_ticket(cassette, connector: TdxConnector):
    in_json = {
            "appid": "fceeaac1-8f96-46d6-9c3b-896e363eb004",
            "identifier": "create_ticket",
            "parameters": [{
                "priority": "Low",
                "requestor_netid": os.environ.get('TDX_NETID', CASSETTE_NETID),
                "title": "NewBoo",
                "type": "Security Support",
                "notify": False,
                "status": "Resolved",
            }],
    }

    result = json.loads(connector._handle_action(json.dumps(in_json), None))

    if not VCR_RECORD:  # Tests only valid when not recording
        assert result[0]["data"][0]["id"] == 564073

    assert result[0]["message"] == "New ticket created"
