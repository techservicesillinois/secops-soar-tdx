# Contributing

```
git clone git@github.com:techservicesillinois/secops-soar-tdx.git

cd secops-soar-tdx

pyenv install 3.9.11
pyenv local 3.9.11

python -m venv venv
source venv/bin/activate

pip install -r requirements-test.txt

pytest
```

If there's changes that require recreating cassettes, set the necessary environment variables:

```sh
export TDX_USERNAME="{api username}"
export TDX_PASSWORD="{password}"

export VCR_RECORD=true

export TDX_NETID="{netid}" # Sets requestor to a valid ID on create_ticket.
export TDX_APPID=66
# Do not set ORGNAME or it will override endpoint.
export TDX_ENDPOINT="help.uillinois.edu"
export TDX_TIMEZONE='-0500'
export TDX_LOGLEVEL='ERROR'
export CLEAN_STRINGS='Edward Delaporte,delaport'
```

To record a cassette, set `VCR_RECORD` in the environment as needed.

```sh
export VCR_RECORD=True
```

TDX Ticket Types:

```
Security Support
CSOC
Generic
```

## Deployment

In GitHub, under 
`Secrets` then `Actions` add the following `Repository Secrets`:

`SOAR_HOSTNAME` set to `automate-illinois.soar.splunkcloud.com`
`SOAR_TOKEN` with your SOAR API token.

### Debugging Deployment

To read deploy logs, visit SOAR `Administration`, and look under `System Health` and then `Debugging`.

## GitHub Actions Setup for Splunk SOAR Deployment

This document guides you through the setup process for GitHub Actions to automatically deploy your application to Splunk SOAR using the provided `.yaml` file in the repository. To achieve this, you will need to configure a couple of secrets in your GitHub repository which will be used by the GitHub Actions pipeline.

### Prerequisites

- You must have admin permissions to the GitHub repository to configure secrets.
- You must have access to your Splunk SOAR instance and the ability to generate an API token.

### Step-by-Step Guide

#### 1. Obtain Splunk SOAR Credentials

Obtain the following credentials from your Splunk SOAR instance:

- `SOAR_TOKEN`: The API token used for authenticating with the Splunk SOAR API
- `SOAR_HOSTNAME`: The hostname (URL) of your Splunk SOAR instance

#### 2. Configure Secrets in GitHub
1. Create a GitHub secret with the name `SOAR_TOKEN` and paste the API token obtained from Splunk SOAR as its value
2. Create another GitHub variable with the name `SOAR_HOSTNAME` and paste the hostname of your Splunk SOAR instance as its value

#### 3. Validate GitHub Actions Workflow

1. Once the secrets are configured, make a change in your repository or manually trigger the GitHub Actions workflow
2. Go to the `Actions` tab in your repository to see the workflow running
3. If everything is configured correctly, you should see the workflow completing successfully
