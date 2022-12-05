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
export TDX_PASSWORD="{password}"
export TDX_USERNAME="techsvc-securityapi"
export TDX_NETID="{netid}" # A valid TDX user on your instance
```

To record a cassette, set `VCRMODE` in the environment as needed.

```sh
export VCRMODE=once
```

TDX Ticket Types:

```
Security Support
CSOC
Generic
```
