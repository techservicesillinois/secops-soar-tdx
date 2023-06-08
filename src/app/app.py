#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------
# Phantom sample App Connector python file
# -----------------------------------------

# Python 3 Compatibility imports
from __future__ import print_function, unicode_literals

# Phantom App imports
import phantom.app as phantom
from phantom.base_connector import BaseConnector
from phantom.action_result import ActionResult

# Usage of the consts file is recommended
# from tdx_consts import *
import requests
import json
from bs4 import BeautifulSoup

# Third-party
import tdxlib
from tdxlib import tdx_api_exceptions as tdx_ex

__version__ = 'GITHUB_TAG'
__git_hash__ = 'GITHUB_SHA'
__deployed__ = 'GITHUB_DEPLOYED'


class RetVal(tuple):

    def __new__(cls, val1, val2=None):
        return tuple.__new__(RetVal, (val1, val2))


class TdxConnector(BaseConnector):

    def __init__(self):

        # Call the BaseConnectors init first
        super(TdxConnector, self).__init__()

        self._state = None

    def _process_empty_response(self, response, action_result):
        if response.status_code == 200:
            return RetVal(phantom.APP_SUCCESS, {})

        return RetVal(
            action_result.set_status(
                phantom.APP_ERROR,
                "Empty response and no information in the header"
            ), None
        )

    def _process_html_response(self, response, action_result):
        # An html response, treat it like an error
        status_code = response.status_code

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            error_text = soup.text
            split_lines = error_text.split('\n')
            split_lines = [x.strip() for x in split_lines if x.strip()]
            error_text = '\n'.join(split_lines)
        except Exception:
            error_text = "Cannot parse error details"

        message = "Status Code: {0}. Data from server:\n{1}\n" \
                  .format(status_code, error_text)

        message = message.replace(u'{', '{{').replace(u'}', '}}')
        return RetVal(action_result.set_status(phantom.APP_ERROR, message),
                      None)

    def _process_json_response(self, r, action_result):
        # Try a json parse
        try:
            resp_json = r.json()
        except Exception as e:
            return RetVal(
                action_result.set_status(
                    phantom.APP_ERROR,
                    "Unable to parse JSON response. Error: {0}".format(str(e))
                ), None
            )

        # Please specify the status codes here
        if 200 <= r.status_code < 399:
            return RetVal(phantom.APP_SUCCESS, resp_json)

        # You should process the error returned in the json
        message = "Error from server. Status Code: {0} Data from server: {1}" \
            .format(
                r.status_code,
                r.text.replace(u'{', '{{').replace(u'}', '}}')
            )

        return RetVal(action_result.set_status(phantom.APP_ERROR, message),
                      None)

    def _process_response(self, r, action_result):
        # store the r_text in debug data,
        # it will get dumped in the logs if the action fails
        if hasattr(action_result, 'add_debug_data'):
            action_result.add_debug_data({'r_status_code': r.status_code})
            action_result.add_debug_data({'r_text': r.text})
            action_result.add_debug_data({'r_headers': r.headers})

        # Process each 'Content-Type' of response separately

        # Process a json response
        if 'json' in r.headers.get('Content-Type', ''):
            return self._process_json_response(r, action_result)

        # Process an HTML response, Do this no matter what the api talks.
        # There is a high chance of a PROXY in between phantom and the rest of
        # world, in case of errors, PROXY's return HTML, this function parses
        # the error and adds it to the action_result.
        if 'html' in r.headers.get('Content-Type', ''):
            return self._process_html_response(r, action_result)

        # it's not content-type that is to be parsed, handle an empty response
        if not r.text:
            return self._process_empty_response(r, action_result)

        # everything else is actually an error at this point
        message = "Can't process response from server." \
                  "Status Code: {0} Data from server: {1}" \
            .format(
                r.status_code,
                r.text.replace('{', '{{').replace('}', '}}')
            )

        return RetVal(action_result.set_status(phantom.APP_ERROR, message),
                      None)

    def _handle_test_connectivity(self, param):
        action_result = self.add_action_result(ActionResult(dict(param)))
        self.save_progress("Connecting to endpoint")
        # Note: There was an `auth` call when the `tdx` object was created.
        # This call results in a second call to `auth`
        success = self.tdx.auth()

        action_result.add_data({})

        if success:
            self.save_progress("Test Connectivity Passed")
            return action_result.set_status(
                phantom.APP_SUCCESS, "Active connection")
        else:
            self.save_progress("Test Connectivity Failed")
            return action_result.set_status(
                phantom.APP_ERROR, "Failed connection")

    def _handle_create_ticket(self, param):
        self.save_progress("In action handler for: {0}".format(
            self.get_action_identifier()))

        # Add an action result object to self (BaseConnector)
        # to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        tdx = self.tdx

        try:
            ticket = tdxlib.tdx_ticket.TDXTicket(tdx, {
                "AccountID": tdx.get_account_by_name(self.account_name)['ID'],
                "PriorityID": tdx.get_ticket_priority_by_name_id(
                    param['priority'])['ID'],
                "RequestorUid": tdx.get_person_by_name_email(
                    param['requestor'])['UID'],
                "Title": param['title'],
                "TypeID": tdx.get_ticket_type_by_name_id(param['type'])['ID'],
            })
            response = tdx.create_ticket(ticket, silent=(not param['notify']))
        except Exception as ex:
            if ex.__class__.__name__ not in dir(tdx_ex):
                raise ex  # Raise unexpected exceptions
            return action_result.set_status(phantom.APP_ERROR,
                                            f"Create ticket failed: {str(ex)}")

        keys = ["ID"]
        action_result.add_data(
            {k.lower(): response.ticket_data[k] for k in keys})

        return action_result.set_status(phantom.APP_SUCCESS,
                                        "Create ticket succeeded")

    def _handle_update_ticket(self, param):
        self.save_progress("In action handler for: {0}".format(
            self.get_action_identifier()))

        # Add an action result object to self (BaseConnector)
        # to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        tdx = self.tdx

        update_args = param
        try:
            _ = tdx.update_ticket(**update_args)
        except Exception as ex:
            if ex.__class__.__name__ not in dir(tdx_ex):
                raise ex  # Raise unexpected exceptions
            return action_result.set_status(phantom.APP_ERROR,
                                            f"Ticket update failed: {str(ex)}")

        return action_result.set_status(phantom.APP_SUCCESS, "Ticket updated")

    def handle_action(self, param):
        ret_val = phantom.APP_ERROR

        # Get the action that we are supposed to execute for this App Run
        action_id = self.get_action_identifier()

        self.debug_print("action_id", self.get_action_identifier())
        self.debug_print("git_hash", __git_hash__)

        if action_id == 'create_ticket':
            ret_val = self._handle_create_ticket(param)

        if action_id == 'update_ticket':
            ret_val = self._handle_update_ticket(param)

        if action_id == 'test_connectivity':
            ret_val = self._handle_test_connectivity(param)

        return ret_val

    def initialize(self):
        # Load the state in initialize, use it to store data
        # that needs to be accessed across actions
        self._state = self.load_state()

        # get the asset config
        config = self.get_config()
        """
        # Access values in asset config by the name

        # Required values can be accessed directly
        required_config_name = config['required_config_name']

        # Optional values should use the .get() function
        optional_config_name = config.get('optional_config_name')
        """

        self.account_name = "None/Not found"  # TODO: pull from config

        self.tdx = tdxlib.tdx_ticket_integration.TDXTicketIntegration(
            config={
                "full_host": config['endpoint'],
                "sandbox": config['sandbox'],
                "username": config['username'],
                "password": config['password'],
                "ticketAppId": config['appid'],
                "assetAppId": "",
                "caching": False,
                "timezone": config['timezone'],
                "logLevel": config['loglevel'],
            })

        return phantom.APP_SUCCESS

    def finalize(self):
        # Save the state, this data is saved across actions and app upgrades
        self.save_state(self._state)
        return phantom.APP_SUCCESS


def main():
    import argparse

    argparser = argparse.ArgumentParser()

    argparser.add_argument('input_test_json', help='Input Test JSON file')
    argparser.add_argument('-u', '--username', help='username', required=False)
    argparser.add_argument('-p', '--password', help='password', required=False)

    args = argparser.parse_args()
    session_id = None

    username = args.username
    password = args.password

    if username is not None and password is None:

        # User specified a username but not a password, so ask
        import getpass
        password = getpass.getpass("Password: ")

    if username and password:
        try:
            login_url = TdxConnector._get_phantom_base_url() + '/login'

            print("Accessing the Login page")
            r = requests.get(login_url, verify=False)
            csrftoken = r.cookies['csrftoken']

            data = dict()
            data['username'] = username
            data['password'] = password
            data['csrfmiddlewaretoken'] = csrftoken

            headers = dict()
            headers['Cookie'] = 'csrftoken=' + csrftoken
            headers['Referer'] = login_url

            print("Logging into Platform to get the session id")
            r2 = requests.post(login_url, verify=False,
                               data=data, headers=headers)
            session_id = r2.cookies['sessionid']
        except Exception as e:
            print("Unable to get session id from the platform. Error: "
                  + str(e))
            exit(1)

    with open(args.input_test_json) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = TdxConnector()
        connector.print_progress_message = True

        if session_id is not None:
            in_json['user_session_token'] = session_id
            connector._set_csrf_info(csrftoken, headers['Referer'])

        ret_val = connector._handle_action(json.dumps(in_json), None)
        print(json.dumps(json.loads(ret_val), indent=4))

    exit(0)


if __name__ == '__main__':
    main()
