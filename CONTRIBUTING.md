# Contributing

```
git clone git@github.com:techservicesillinois/secops-soar-tdx.git

cd secops-soar-tdx

pyenv install 3.9.11
pyenv local 3.9.11

python -m venv venv
source venv/bin/activate

pip install wheel
pip install -r requirements-test.txt

pytest
```
