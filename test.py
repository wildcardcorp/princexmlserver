import requests
import json

resp = requests.post('http://127.0.0.1:6543/convert', data={
    'doctype': 'html',
    'xml': '<html><body><h1>Foobar</h1></body></html>',
    'css': [json.dumps(['h1{color: red} body{background-color:lime}'])],
})
with open('test.pdf', 'wb') as fout:
    fout.write(resp.text.encode('utf-8'))
