import json
import os

from app.app import TdxConnector
from conftest import CASSETTE_NETID

APP_ID = "tacosalad"
#  TICKET_ID must match ticket ID found in
#  cassettes/test_reassign_user.yaml
#  cassettes/test_reassign_group.yaml

#  PROTIP: After the TDX Sandbox environment gets reset, you'll have to
#  go digging for a new ticket ID in order to re-record these cassettes.
TICKET_ID = 1011312


def test_reassign_group(cassette, connector: TdxConnector):
    in_json = {
        "appid": APP_ID,
        "identifier": "reassign_group",
        "parameters": [{
            "ticket_id": TICKET_ID,
            "responsible": "UIUC-TechServices-Cybersecurity Developers"
        }],
    }

    result = json.loads(connector._handle_action(json.dumps(in_json), None))

    assert result[0]["message"] == "Ticket reassigned"
    # TODO: Implement reassign in connector and json
    # ticket_id: Union[str, int]
    # responsible: str
    # group: bool


def test_reassign_user(cassette, connector: TdxConnector):
    in_json = {
        "appid": APP_ID,
        "identifier": "reassign_user",
        "parameters": [{
            "ticket_id": TICKET_ID,
            "responsible": os.environ.get('TDX_NETID', CASSETTE_NETID),
        }],
    }

    result = json.loads(connector._handle_action(json.dumps(in_json), None))

    assert result[0]["message"] == "Ticket reassigned"
