import json
import os
import sys
from urllib.error import HTTPError

import pytest
import vcr

from unittest.mock import patch, Mock
from requests.exceptions import HTTPError

from phTDX.tdx_connector import TdxConnector



def test_connectivity(cassette, connector: TdxConnector):
    in_json = {
            "appid": "fceeaac1-8f96-46d6-9c3b-896e363eb004",
            "identifier": "test_connectivity",
            "parameters": [{}], # TODO: Submit an issue asking to allow [] here.
    }

    # with pytest.raises(HTTPError):
    result = json.loads(connector._handle_action(json.dumps(in_json), None))

    assert result[0]["message"] == "Active connection"
    # TODO: Once we have a cassette, let's enforce it's use.
    #  Ideally in conftest.py
    #  and using the cassette's existence to decide...
    assert cassette.all_played
    # assert cassette.play_count == 1
    # TODO: Submit a bug to tdxlib - bad password becomes TypeError
    #    should be raised as an auth error
    #
    #  "Authorization": 'Bearer ' + self.token,
        # TypeError: can only concatenate str (not "NoneType") to str
    # ==================================== short test summary info =====================================
    # FAILED tests/test_connector.py::test_connectivity - TypeError: can only concatenate str (not "N...


def test_create_ticket(cassette, connector: TdxConnector):
    in_json = {
            "appid": "fceeaac1-8f96-46d6-9c3b-896e363eb004",
            "identifier": "create_ticket",
            "parameters": [{
                "priority": "Low",
                "requestor_netid": "buch1",
                "title": "NewBoo",
                "type": "Security Support",
                "notify": False,
                "status": "Resolved",
            }],
    }

    # with pytest.raises(HTTPError):
    result = json.loads(connector._handle_action(json.dumps(in_json), None))

    # assert response.ticket_data['ID'] == response.get_id()
    assert result[0]["message"] == f"New ticket created"
    assert cassette.all_played  # Move to conftest.py
    # assert cassette.play_count == 1
