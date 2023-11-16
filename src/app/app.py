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


# Third-party
import tdxlib
from tdxlib import tdx_api_exceptions as tdx_ex

__version__ = 'GITHUB_TAG'
__git_hash__ = 'GITHUB_SHA'
__deployed__ = 'BUILD_TIME'


class OrgNameAndEndpointSet(Exception):
    def __init__(self):
        super().__init__(
            "'Organization Name' and 'endpoint' cannot both be set.")


class OrgNameAndEndpointNotSet(Exception):
    def __init__(self):
        super().__init__(
            "You must set either 'Organization Name' or 'endpoint'.")


class RetVal(tuple):

    def __new__(cls, val1, val2=None):
        return tuple.__new__(RetVal, (val1, val2))


class TdxConnector(BaseConnector):

    def __init__(self):

        # Call the BaseConnectors init first
        super(TdxConnector, self).__init__()

        self._state = None

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
            params = {
                "AccountID": tdx.get_account_by_name(self.account_name)['ID'],
                "PriorityID": tdx.get_ticket_priority_by_name_id(
                    param['priority'])['ID'],
                "RequestorUid": tdx.get_person_by_name_email(
                    param['requestor'])['UID'],
                "Title": param['title'],
                "TypeID": tdx.get_ticket_type_by_name_id(param['type'])['ID'],
                # TODO: Find a programmatic way to determine the ID to send
                # for the TLP Attribute
                "Attributes": [{"ID": "4363", "Value": param['TLP']}],
            }

            if "description" in param and param["description"]:
                params["Description"] = param["description"]

            ticket = tdxlib.tdx_ticket.TDXTicket(tdx, params)
            response = tdx.create_ticket(ticket, silent=(not param['notify']))
        except Exception as ex:
            if ex.__class__.__name__ not in dir(tdx_ex):
                raise ex  # Raise unexpected exceptions
            return action_result.set_status(phantom.APP_ERROR,
                                            f"Create ticket failed: {str(ex)}")

        keys = ["ID"]
        action_result.add_data(
            {k.lower(): response.ticket_data[k] for k in keys})

        return action_result.set_status(
            phantom.APP_SUCCESS, "Create ticket succeeded")

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
            return action_result.set_status(
                phantom.APP_ERROR, f"Ticket update failed: {str(ex)}")

        return action_result.set_status(phantom.APP_SUCCESS, "Ticket updated")

    def _handle_reassign_group(self, param):
        return self._handle_reassign(param, group=True)

    def _handle_reassign_user(self, param):
        return self._handle_reassign(param, group=False)

    def _handle_reassign(self, param, group=False):
        self.save_progress("In action handler for: {0}".format(
            self.get_action_identifier()))

        # Add an action result object to self (BaseConnector)
        # to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        tdx = self.tdx
        update_args = param

        try:
            _ = tdx.reassign_ticket(group=group, **update_args)
        except Exception as ex:
            if ex.__class__.__name__ not in dir(tdx_ex):
                raise ex  # Raise unexpected exceptions
            return action_result.set_status(
                phantom.APP_ERROR, f"Ticket reassignment failed: {str(ex)}")

        return action_result.set_status(
            phantom.APP_SUCCESS, "Ticket reassigned")

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

        if action_id == 'reassign_group':
            ret_val = self._handle_reassign_group(param)

        if action_id == 'reassign_user':
            ret_val = self._handle_reassign_user(param)

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

        tdxlib_config = {
            "full_host": config.get('endpoint', ''),
            "org_name": config.get('orgname', ''),
            "sandbox": config['sandbox'],
            "username": config['username'],
            "password": config['password'],
            "ticket_app_id": config['appid'],
            "asset_app_id": "",
            "caching": False,
            "timezone": config['timezone'],
            "logLevel": config['loglevel'],
        }

        if tdxlib_config['org_name'] and tdxlib_config['full_host']:
            raise OrgNameAndEndpointSet()

        if not (tdxlib_config['org_name'] or tdxlib_config['full_host']):
            raise OrgNameAndEndpointNotSet()

        self.tdx = tdxlib.tdx_ticket_integration.TDXTicketIntegration(
            config=tdxlib_config)

        return phantom.APP_SUCCESS
