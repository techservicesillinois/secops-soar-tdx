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
export TDX_ENDPOINT="help.uillinois.edu"
export TDX_ORGNAME='University of Illinois'  # Does not seem to matter.
export TDX_TIMEZONE='-0500'
export TDX_LOGLEVEL='ERROR'
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