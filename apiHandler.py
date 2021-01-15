import json
import requests

def apiCallReturnJSON(method, url, token, content_type, payload):

    # TODO: Check if the token is still valid

    print("Token: {}".format(token))

    headers = {
    'Content-Type': content_type,
    'Authorization': 'Bearer {}'.format(token)
    }

    response = requests.request(method, url, headers=headers, data=payload)
    print("Response Status: {} \n".format(response))
    
    return json.loads(response.text)