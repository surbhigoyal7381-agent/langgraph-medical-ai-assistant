import requests, time, json
url='http://127.0.0.1:8001/chat'
payload={'message':'test streaming','patient_id':'test-patient','thread_id':'test-thread'}
print('POSTing to', url)
try:
    with requests.post(url, json=payload, stream=True, timeout=30) as r:
        print('status', r.status_code)
        if r.status_code!=200:
            print('non-200')
        for line in r.iter_lines():
            if not line: continue
            s=line.decode()
            print('LINE:',s[:200])
            if s.startswith('data:'):
                try:
                    obj=json.loads(s.replace('data:','').strip())
                    print('EVENT',obj.get('type'), 'chunklen', len(obj.get('chunk','')))
                    if obj.get('type')=='end':
                        print('END')
                        break
                except Exception as e:
                    print('parse err', e)
    print('done')
except Exception as e:
    print('request failed', e)
