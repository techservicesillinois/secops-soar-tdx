import json
import os

from app.app import TdxConnector

from conftest import VCR_RECORD, CASSETTE_NETID

APP_ID = "tacosalad"
TICKET_ID = 564073  # Must match cassette


def test_connectivity(cassette, connector: TdxConnector):
    in_json = {
        "appid": APP_ID,
        "identifier": "test_connectivity",
        # TODO: Submit an issue asking to allow [] here.
        "parameters": [{}],
    }

    result = json.loads(connector._handle_action(json.dumps(in_json), None))
    assert result[0]["message"] == "Active connection"


def test_failed_connectivity(cassette, connector: TdxConnector):
    in_json = {
        "appid": APP_ID,
        "identifier": "test_connectivity",
        "parameters": [{}],
    }
    # BEWARE: You can uncomment this line to force a 403, but leaving it 
    # uncommented while recording will lock out our test account.
    # connector.config['password'] = 'this_is_nonsense'
    result = json.loads(connector._handle_action(json.dumps(in_json), None))
    assert result[0]["message"] == "Failed connection"


def test_create_ticket(cassette, connector: TdxConnector):
    in_json = {
        "appid": APP_ID,
        "identifier": "create_ticket",
        "parameters": [{
            "priority": "Low",
            "requestor": os.environ.get('TDX_NETID', CASSETTE_NETID),
            "title": "NewBoo",
            "type": "Security Support",
            "notify": False,
            "status": "Resolved",
        }],
    }

    result = json.loads(connector._handle_action(json.dumps(in_json), None))

    if not VCR_RECORD:  # Tests only valid when not recording
        assert result[0]["data"][0]["id"] == 564073

    assert result[0]["message"] == "Create ticket succeeded"


def test_failed_create(cassette, connector: TdxConnector):
    in_json = {
        "appid": APP_ID,
        "identifier": "create_ticket",
        "parameters": [{
            "priority": "Low",
            "requestor": "no_such_user",
            "title": "NewBoo",
            "type": "No Such Type",
            "notify": False,
            "status": "Resolved",
        }],
    }

    result = json.loads(connector._handle_action(json.dumps(in_json), None))

    assert result[0]["message"] == \
        "Create ticket failed: No person found for no_such_user"


def test_update_ticket(cassette, connector: TdxConnector):
    in_json = {
        "appid": APP_ID,
        "identifier": "update_ticket",
        "parameters": [{
            "ticket_id": TICKET_ID,
            "comments": "This is a test comment.",
            "new_status": "Resolved",
            "notify": [],
            "private": False,
        }],
    }

    result = json.loads(connector._handle_action(json.dumps(in_json), None))

    assert result[0]["message"] == "Ticket updated"


def test_failed_update(cassette, connector: TdxConnector):
    in_json = {
        "appid": APP_ID,
        "identifier": "update_ticket",
        "parameters": [{
            "ticket_id": TICKET_ID,
            "comments": "This is a test comment.",
            "new_status": "GARBAGE",
            "notify": [],
            "private": False,
        }],
    }

    result = json.loads(connector._handle_action(json.dumps(in_json), None))

    assert result[0]["message"] == \
        "Ticket update failed: No status found for GARBAGE"
