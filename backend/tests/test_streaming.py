import requests
import json
import time

url='http://127.0.0.1:8000/chat'
payload={'message':'test streaming','patient_id':'test-patient','thread_id':'test-thread'}

print('POSTing to', url)
with requests.post(url, json=payload, stream=True, timeout=30) as r:
    print('status', r.status_code)
    assert r.status_code==200
    decoder = r.iter_lines()
    received_chunks=0
    start=time.time()
    for raw in decoder:
        if not raw:
            continue
        line = raw.decode(errors='ignore')
        if line.startswith('data:'):
            try:
                obj=json.loads(line.replace('data:','').strip())
                print('event type=', obj.get('type'), 'chunk=', obj.get('chunk','')[:60])
                if obj.get('type')=='chunk':
                    received_chunks += 1
                if obj.get('type')=='end':
                    print('stream end')
                    break
            except Exception as e:
                print('json parse error', e)
    elapsed=time.time()-start
    print('received', received_chunks, 'chunks in', elapsed, 's')
    assert received_chunks>0
print('streaming test passed')
