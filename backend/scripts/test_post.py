import sys
import json
from urllib import request, error

url = 'http://127.0.0.1:8000/chat'
data = json.dumps({"message":"hello","patient_id":"1","thread_id":"1"}).encode('utf-8')
req = request.Request(url, data=data, headers={'Content-Type':'application/json'}, method='POST')
try:
    with request.urlopen(req, timeout=10) as resp:
        print('Status:', resp.status)
        headers = dict(resp.getheaders())
        print('Headers:', headers)
        # Read a bit of body
        chunk = resp.read(1024)
        print('Body chunk:', chunk[:200])
except error.HTTPError as e:
    print('HTTPError:', e.code, e.reason)
    try:
        print(e.read().decode())
    except Exception:
        pass
except Exception as e:
    print('Exception:', repr(e))
    sys.exit(1)
else:
    sys.exit(0)
