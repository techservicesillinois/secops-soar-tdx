import os
import sys
import logging

# Add root directory to path
sys.path.insert(0, os.getcwd()) 

import pytest
# Load pytest-splunk-soar-connectors plugin
pytest_plugins = ("splunk-soar-connectors")

# Replace this with the import for your connector
from phtdx.tdx_connector import TDXConnector

#TODO Mock environment variables BHR_HOST and BHR_TOKEN
@pytest.fixture(scope='function')
def connector():
    conn = TDXConnector()

    # Define the asset configuration to be used 
    # conn.config = {
    # }

    conn.logger.setLevel(logging.INFO)
    return conn
