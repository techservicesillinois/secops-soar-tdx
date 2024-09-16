#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------
# Phantom sample App Connector python file
# -----------------------------------------

# Python 3 Compatibility imports
from __future__ import print_function, unicode_literals

# Phantom App imports
import inspect
import phantom.app as phantom
# from phtoolbox.app.base_connector import NiceBaseConnector, handle
from phantom.action_result import ActionResult
from phantom.base_connector import BaseConnector


# Third-party
import tdxlib
from tdxlib import tdx_api_exceptions as tdx_ex

__version__ = 'GITHUB_TAG'
__git_hash__ = 'GITHUB_SHA'
__deployed__ = 'BUILD_TIME'

# Custom Attribute 'UIUC-TechSvc-Security TLP' has ID 4363
TLP_ID = "4363"
# Custom Attribute 'UIUC-TechSvc-CSOC Incident Severity' has ID 4902
SEVERITY_ID = "4902"
# Ticket Type 'CSOC' has ID 310
TYPE_ID = 310

TLP_TABLE = {
    "CLEAR": "8175",
    "GREEN": "8174",
    "AMBER": "8173",
    "AMBER+STRICT": "14037",
    "RED": "8172",
}

SEVERITY_TABLE = {
    "TO BE DETERMINED": "10539",
    "NON-EVENT": "10541",
    "LOW": "10540",
    "MEDIUM": "10203",
    "HIGH": "10204",
    "CRITICAL": "10542",
}


# start of base_connector.py

# -----------------------------------------
# Nice and dry Phantom App
# -----------------------------------------


def handle(*action_ids):
    """Registor function to handle given action_ids."""
    def decorator(func):
        func._handle = action_ids
        return func
    return decorator


class NiceBaseConnector():

    def __init__(self, app_success_code, app_error_code):
        self.__version__ = 'UNSET_VERSION - set self.__version__ to emit here'
        self.__git_hash__ = \
            'UNSET_GIT_HASH - set self.__git_hash__ to emit here'
        self.__build_time__ = \
            'UNSET_BUILD_TIME - set self.__build_time__ to emit here'

        self.actions = {}
        for _, method in inspect.getmembers(self):
            if hasattr(method, '_handle'):
                for action_id in getattr(method, '_handle'):
                    self.actions[action_id] = method

        self._state = None
        self._app_success = app_success_code
        self._app_error = app_error_code

    def nice_handle_action(self, param):
        """A function to implement handle_action.
        The handle_action method MUST be defined in the child class."""
        action_id = self.get_action_identifier()
        self.debug_version_info()
        self.debug_print("action_id", self.get_action_identifier())

        if action_id in self.actions.keys():
            return self.actions[action_id](param)

        return self._app_error

    def debug_version_info(self):
        """ Developers are encouraged to set the following values:
            - self.__version__ = 'GITHUB_TAG'
            - self.__git_hash__ = 'GITHUB_SHA'
            - self.__build_time__ = 'BUILD_TIME'
        """

        self.debug_print("Version: " + self.__version__)
        self.debug_print("Git Hash: " + self.__git_hash__)
        self.debug_print("Build Time:" + self.__build_time__)

    def initialize(self):
        # Load the state in initialize, use it to store data
        # that needs to be accessed across actions
        self._state = self.load_state()
        return self._app_success

    def finalize(self):
        # Save the state, this data is saved across actions and
        # app upgrades
        self.save_state(self._state)
        return self._app_success
# end of base_connector.py


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
                if 'type' in param else TYPE_ID,
                "Attributes": [
                    {"ID": TLP_ID, "Value": TLP_TABLE[param["TLP"].upper()]},
                    {"ID": SEVERITY_ID,
                     "Value": SEVERITY_TABLE[param["severity"].upper()]},
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
