import requests
import json

#Authenticate (must be run before any subsequent API calls)
def tdx_test_connection():
    return True
#    my_headers = {'Content-Type' : 'application/json'}

    #Need a .env file to define TDX_USERNAME and TDX_PASSWORD
#    query = {'username': config['TDX_USERNAME'], 'password': config['TDX_PASSWORD']}
#    response = requests.post(f'{config["TDX_ENDPOINT"]}/api/auth', headers=my_headers, data=json.dumps(query))
 #   
 #   return response.status_code == requests.codes.ok
        
    
#token = response.text
#my_headers['Authorization'] = f"Bearer {token}"


#appid = os.environ['TDX_APPID']
#enablenotifyreviewer = False
#notifyrequestor = False
#notifyresponsible = False
#allowrequestorcreation = False
#query = {'Title':'New Closed Ticket'}
#uri = f"https://help.uillinois.edu/SBTDWebApi/api/{appid}/tickets?EnableNotifyReviewer={enablenotifyreviewer}&NotifyRequestor={notifyrequestor}&NotifyResponsible={notifyresponsible}&AllowRequestorCreation={allowrequestorcreation}"

#response = requests.post(uri, headers=my_headers, data=json.dumps(query))