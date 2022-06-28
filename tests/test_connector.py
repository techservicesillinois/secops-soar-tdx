import json
import os
import sys
from urllib.error import HTTPError

import pytest
import vcr

from unittest.mock import patch, Mock
from requests.exceptions import HTTPError

from phTDX.tdx_connector import TdxConnector



def test_connectivity_fail(cassette, connector: TdxConnector):
    in_json = {
            "appid": "fceeaac1-8f96-46d6-9c3b-896e363eb004",
            "identifier": "test_connectivity",
            "parameters": {
            }
    }

    # with pytest.raises(HTTPError):
    action_result_str = connector._handle_action(json.dumps(in_json), None)

    # assert cassette.all_played
    # assert cassette.play_count == 1
