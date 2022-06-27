import json
import os
import requests
import tdxlib
# from dotenv import load_dotenv
from pprint import PrettyPrinter

# Authenticate (must be run before any subsequent API calls)
# load_dotenv()
# def get_token():
#    my_headers = {'Content-Type' : 'application/json'}
#    query = {'username':os.environ['TDX_USERNAME'], 'password':os.environ['TDX_PASSWORD']}
#    response = requests.post('https://help.uillinois.edu/SBTDWebApi/api/auth', headers=my_headers, data=json.dumps(query))
#    token = response.text
#    return token


# def test_tdx_create_ticket(cassette):
#     tdx = tdxlib.tdx_ticket_integration.TDXTicketIntegration('tdxlib.ini')
#     json_dict = {
#         "AccountID": 7902,
#         "PriorityID": 24,
#         "RequestorUid": tdx.get_person_by_name_email('buch1')['UID'],
#         "Title": "Boo",
#         "TypeID": 292,
#     }
#     ticket = tdxlib.tdx_ticket.TDXTicket(tdx, json_dict)
#     response = tdx.create_ticket(ticket)
#     assert response.ticket_data['ID'] == 216780


# def test_tdx_update_ticket(cassette):
#     tdx = tdxlib.tdx_ticket_integration.TDXTicketIntegration('tdxlib.ini')
#     response = tdx.update_ticket(216780, "Updated Ticket", "Resolved")
#     assert response['ID'] == 911867


def test_tdx_integration_from_config(cassette):
    config = { 
        'TDX API Settings': {
            "orgname": "myuniversity",
            "fullhost": "help.uillinois.edu",
            "sandbox": True,
            "username": "techsvc-securityapi",
            "ticketAppId": 66,
            "assetAppId": "",
            "caching": False,
            "timezone": "-0500",
            "logLevel": "ERROR",
    }}
    tdx = tdxlib.tdx_ticket_integration.TDXTicketIntegration(config=config)
