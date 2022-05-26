import json
import os
import sys

import pytest

from unittest.mock import patch, Mock

from phtdx.tdx_connector import TDXConnector
from bhr_client.rest import Client as BHRClient

@patch("phtdx.tdx_connector.login_from_env")
def test_connectivity(mock, connector: TDXConnector):
    mock.return_value = Mock(spec=BHRClient)
    in_json = {
            "appid": "fceeaac1-8f96-46d6-9c3b-896e363eb004",
            "parameters": {
                "identifier": "test_connectivity",
            }
    }

    # Execute Action
    action_result_str = connector._handle_action(json.dumps(in_json), None)
    action_result = json.loads(action_result_str)

    # Assertion
    assert action_result[0]["message"] == "Active connection"
    mock.return_value.query.assert_called_once()

@patch("phtdx.tdx_connector.login_from_env")
def test_block(mock, connector: TDXConnector):
    cidr = '157.55.39.89/32'

    mock.return_value = Mock(spec=BHRClient)
    in_json = {
            "appid": "fceeaac1-8f96-46d6-9c3b-896e363eb004",
            "parameters": {
                "identifier": "block",
                "cidr": cidr,
            }
    }

    # Execute Action
    dump = json.dumps(in_json)
    import pdb; pdb.set_trace()
    action_result_str = connector._handle_action(dump, None)
    action_result = json.loads(action_result_str)

    # Assertion
    assert action_result[0]["message"] == f"Blocked {cidr}"
    mock.return_value.block.assert_called_once()
    assert 'cidr' in mock.call_args.kwargs
    assert mock.call_args.kwargs['cidr'] == cidr
