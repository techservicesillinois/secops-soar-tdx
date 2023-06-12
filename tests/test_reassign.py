import json
from app.app import TdxConnector

APP_ID = "tacosalad"
TICKET_ID = 564073  # Must match cassette


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
            "responsible": "delaport"
        }],
    }

    result = json.loads(connector._handle_action(json.dumps(in_json), None))

    assert result[0]["message"] == "Ticket reassigned"
