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
 

def test_tdx_create_ticket(cassette):
    tdx = tdxlib.tdx_ticket_integration.TDXTicketIntegration('tdxlib.ini')
    # ticket = tdxlib.tdx_ticket.TDXTicket(tdx) 
    ticket_attributes = {'title_template':'test ticket',
    'ticket_type':292,
    'account':'None/Not found',
    'responsible':'buch1',
    'requestor':'buch1',
    }
    ticket = tdx.generate_ticket(**ticket_attributes)
    tdx.create_ticket(ticket)
     # Code dies HERE!
#    ticket.ticket_data['StatusID'] = \
#        ticket.tdx_api.search_ticket_status('Resolved')['ID']
#    ticket.ticket_data['Title'] = "Ticket from unit test"
#
#    results = tdx.create_ticket(new_ticket)
