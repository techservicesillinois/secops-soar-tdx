#!/usr/bin/env python

import base64
import json
import os
import requests
import sys

file_contents = open('soar_app.tgz', 'rb').read()
encoded_contents = base64.b64encode(file_contents)
payload = {'app': encoded_contents.decode('ascii')}
headers = {'ph-auth-token': os.environ['SOAR_TOKEN']}
url=os.environ['SOAR_URL']
result = requests.post(url,
                headers=headers,
                data=json.dumps(payload))

print(result.text)

if result.status_code != requests.codes.ok or 'failed' in result.json():
    sys.exit(1)
