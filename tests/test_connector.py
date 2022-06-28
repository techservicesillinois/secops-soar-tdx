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
    action_result_str = connector._handle_action(json.dumps(in_json), None)

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
