import json
import os
import requests
import tdxlib
# from dotenv import load_dotenv
from pprint import PrettyPrinter

#Authenticate (must be run before any subsequent API calls)
# load_dotenv()
#def get_token():
#    my_headers = {'Content-Type' : 'application/json'}
#    query = {'username':os.environ['TDX_USERNAME'], 'password':os.environ['TDX_PASSWORD']}
#    response = requests.post('https://help.uillinois.edu/SBTDWebApi/api/auth', headers=my_headers, data=json.dumps(query))
#    token = response.text
#    return token
#
#
#def test_token_length(cassette):
#    token = get_token()
#    assert len(token) == 313
    

def test_tdx_connection(cassette):
    tdx = tdxlib.tdx_ticket_integration.TDXTicketIntegration('tdxlib.ini')
    search = tdx.search_tickets("test")
