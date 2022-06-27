import json
import os
import sys
from urllib.error import HTTPError

import pytest
import vcr

from unittest.mock import patch, Mock
from requests.exceptions import HTTPError

from phsoar_tdx_client.soar_tdx_client_connector import Soar_Tdx_ClientConnector


def test_connectivity_fail(cassette, connector: Soar_Null_RouterConnector):
    in_json = {
            "appid": "fceeaac1-8f96-46d6-9c3b-896e363eb004",
            "parameters": {
                "identifier": "test_connectivity",
            }
    }

    with vcr.use_cassette('tests/cassettes/test_connectivity_fail.yaml') as cassette:
        with pytest.raises(HTTPError):
            action_result_str = connector._handle_action(json.dumps(in_json), None)

        assert cassette.all_played
        assert cassette.play_count == 1