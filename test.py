import requests
import json

resp = requests.post('http://127.0.0.1:6543/convert', json={
    'doctype': 'html',
    'additional_args': {
        'pdf_profile': 'PDF/UA-1',
    },
    'xml': """
        <html>
            <head>
                <title>Test Document</title>
            </head>
            <body>
                <h1>Foobar</h1>
                <p>
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed consectetur, neque ut finibus tristique, diam ex finibus diam, a varius lorem ipsum at libero. Nunc a fringilla purus. Vestibulum ac velit volutpat, varius ipsum quis, faucibus tortor. Proin ultrices justo elit, nec pellentesque dolor tincidunt ut. In sed volutpat diam, congue lacinia sem. Aenean vehicula mi sit amet velit faucibus, sit amet convallis ante suscipit. Mauris venenatis lobortis nisi, sed faucibus ante accumsan eu. Nam id neque orci. 
                </p>
            </body>
        </html>

    """,
    'css': [
        """
        h1 {
            color: red
        }

        body {
            background-color: lime
        }
        """
    ],
})
if resp.status_code == 200:
    print("successfully requested pdf, outputing to `test.pdf`")
    with open('test.pdf', 'wb') as fout:
        fout.write(resp.content)
else:
    print(f"failed to generate requested pdf, HTTP {resp.status_code}")
