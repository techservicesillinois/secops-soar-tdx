import json
import os
import pytest

from app.app import TdxConnector
from app.app import OrgNameAndEndpointSet, OrgNameAndEndpointNotSet

from conftest import VCR_RECORD, CASSETTE_NETID

APP_ID = "tacosalad"
#  TICKET_ID must match ticket ID found in
#  cassettes/test_create_ticket.yaml

#  PROTIP: After re-recording test_create_ticket.yaml, update this Ticket ID.
TICKET_ID = 564073
DEFAULT_GROUP = "UIUC-TechServices-Cybersecurity Incident Response"


def test_connectivity(cassette, connector: TdxConnector):
    in_json = {
        "appid": APP_ID,
        "identifier": "test_connectivity",
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
    # connector.config['password'] = 'nonsense'  # pragma: allowlist secret
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
            "type": "CSOC",
            "notify": False,
            "status": "New",
            "description": "",
            "TLP": "Amber",
            "formid": "UIUC-TechSvc-CSOC Incidents",
            "severity": "To Be Determined",
            "responsible":
                "UIUC-TechServices-Cybersecurity Incident Response"
        }],
    }

    raw_result = connector._handle_action(json.dumps(in_json), None)
    result = json.loads(raw_result)

    if not VCR_RECORD:  # Tests only valid when not recording
        assert result[0]["data"][0]["ticket_id"] == 564073

    assert result[0]["message"] == "Create ticket succeeded"
    assert DEFAULT_GROUP in raw_result


def test_create_ticket_defaults(cassette, connector: TdxConnector):
    in_json = {
        "appid": APP_ID,
        "identifier": "create_ticket",
        "parameters": [{
            "priority": "Low",
            "requestor": os.environ.get('TDX_NETID', CASSETTE_NETID),
            "title": "NewBoo",
            "notify": False,
            "description": "",
            "TLP": "Amber",
            "formid": "UIUC-TechSvc-CSOC Incidents",
            "severity": "To Be Determined",
            "responsible":
                "UIUC-TechServices-Cybersecurity Incident Response"
        }],
    }

    raw_result = connector._handle_action(json.dumps(in_json), None)
    result = json.loads(raw_result)

    if not VCR_RECORD:  # Tests only valid when not recording
        assert result[0]["data"][0]["ticket_id"] == 564073

    assert result[0]["message"] == "Create ticket succeeded"
    assert DEFAULT_GROUP in raw_result


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
            "description": "",
            "TLP": "Red",
            "severity": "To Be Determined",
            "formid": "UIUC-TechSvc-CSOC Incidents",
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


def config_set(config, key, value):
    if value:
        config[key] = value
    elif key in config:
        del config[key]


@pytest.mark.parametrize("endpoint,orgname,exception", [
    (None, None, OrgNameAndEndpointNotSet),
    ('foo', 'bar', OrgNameAndEndpointSet),
])
def test_bad_config(endpoint, orgname, exception,
                    cassette, connector: TdxConnector):
    in_json = {
        "appid": APP_ID,
        "identifier": "test_connectivity",
        "parameters": [{}],
    }

    config_set(connector.config, 'endpoint', endpoint)
    config_set(connector.config, 'orgname', orgname)

    with pytest.raises(exception):
        json.loads(connector._handle_action(json.dumps(in_json), None))
