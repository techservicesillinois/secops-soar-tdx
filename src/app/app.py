#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------
# Phantom sample App Connector python file
# -----------------------------------------

# Python 3 Compatibility imports
from __future__ import print_function, unicode_literals

# Phantom App imports
import phantom.app as phantom
from phantom.action_result import ActionResult
from phantom.base_connector import BaseConnector

# Third-party
import tdxlib
from tdxlib import tdx_api_exceptions as tdx_ex
from phtoolbox.app.base_connector import NiceBaseConnector, handle

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


class TdxConnector(BaseConnector, NiceBaseConnector):
    def __init__(self):
        BaseConnector.__init__(self)
        # It acts like BaseConnector does not call super().__init__()
        NiceBaseConnector.__init__(
            self, phantom.APP_SUCCESS, phantom.APP_ERROR)

    def handle_action(self, param):
        # handle_action is an abstract method; it MUST be implemented here.
        self.nice_handle_action(param)

    @handle('test_connectivity')
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

    @handle('create_ticket')
    def _handle_create_ticket(self, param):
        self.save_progress("In action handler for: {0}".format(
            self.get_action_identifier()))

        # Add an action result object to self (NiceBaseConnector)
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
                "TypeID": tdx.get_ticket_type_by_name_id(param['type'])['ID']
                if 'type' in param else self.config['ticket_type_id'],
                "Attributes": [
                    {"ID": self.config['tlp_id'],
                     "Value": self.tlp_table[param["TLP"].upper()]},
                    {"ID": self.config['severity_id'],
                     "Value": self.severity_table[param["severity"].upper()]},
                ],
                "FormID": tdx.get_ticket_form_by_name_id(
                    param['formid'])['ID'],
                "Responsible": param['responsible']
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
            {f"ticket_{k.lower()}": response.ticket_data[k] for k in keys})

        return action_result.set_status(
            phantom.APP_SUCCESS, "Create ticket succeeded")

    @handle('update_ticket')
    def _handle_update_ticket(self, param):
        self.save_progress("In action handler for: {0}".format(
            self.get_action_identifier()))

        # Add an action result object to self (NiceBaseConnector)
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

    @handle('reassign_group')
    def _handle_reassign_group(self, param):
        return self._handle_reassign(param, group=True)

    @handle('reassign_user')
    def _handle_reassign_user(self, param):
        return self._handle_reassign(param, group=False)

    @handle('reassign')
    def _handle_reassign(self, param, group=False):
        self.save_progress("In action handler for: {0}".format(
            self.get_action_identifier()))

        # Add an action result object to self (NiceBaseConnector)
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

    def initialize(self):
        # Load the state in initialize, use it to store data
        # that needs to be accessed across actions
        self._state = self.load_state()

        # self._load_app_json()
        # self.config = self.get_app_config()
        # get the asset config
        self.config = self.get_config()
        """
        # Access values in asset config by the name

        # Required values can be accessed directly
        required_config_name = config['required_config_name']

        # Optional values should use the .get() function
        optional_config_name = config.get('optional_config_name')
        """

        self.account_name = "None/Not found"  # TODO: pull from config
        self.tlp_table = {
            "CLEAR": self.config['tlp_clear_id'],
            "GREEN": self.config['tlp_green_id'],
            "AMBER": self.config['tlp_amber_id'],
            "AMBER+STRICT": self.config['tlp_amberstrict_id'],
            "RED": self.config['tlp_red_id'],
        }

        self.severity_table = {
            "TO BE DETERMINED": self.config['severity_tbd_id'],
            "NON-EVENT": self.config['severity_nonevent_id'],
            "LOW": self.config['severity_low_id'],
            "MEDIUM": self.config['severity_medium_id'],
            "HIGH": self.config['severity_high_id'],
            "CRITICAL": self.config['severity_critical_id'],
        }

        tdxlib_config = {
            "full_host": self.config.get('endpoint', ''),
            "org_name": self.config.get('orgname', ''),
            "sandbox": self.config['sandbox'],
            "username": self.config['username'],
            "password": self.config['password'],
            "ticket_app_id": self.config['appid'],
            "asset_app_id": "",
            "caching": False,
            "timezone": self.config['timezone'],
            "logLevel": self.config['loglevel'],
        }

        if tdxlib_config['org_name'] and tdxlib_config['full_host']:
            raise OrgNameAndEndpointSet()

        if not (tdxlib_config['org_name'] or tdxlib_config['full_host']):
            raise OrgNameAndEndpointNotSet()

        self.tdx = tdxlib.tdx_ticket_integration.TDXTicketIntegration(
            config=tdxlib_config)

        return phantom.APP_SUCCESS
