# Note that setup.py is NOT deprecated, but it should be used sparingly:
# https://packaging.python.org/en/latest/discussions/setup-py-deprecated/#setup-py-deprecated
#
# Best practice is to maintain an empty setup.py file for maximum compatibility:
# https://packaging.python.org/en/latest/guides/modernize-setup-py-project/#should-setup-py-be-deleted
#
# Whenever possible edit pyproject.toml. All static metadata belongs in
# pyproject.toml:
# https://packaging.python.org/en/latest/guides/modernize-setup-py-project/#how-to-handle-packaging-metadata
#
# Only dynamic build time code and dynamic metadata belong here:
# https://packaging.python.org/en/latest/guides/modernize-setup-py-project/#modernize-setup-py-project
import setuptools

setuptools.setup()
