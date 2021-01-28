import json
import requests

def apiCallReturnJSON(method, url, token, content_type, payload):
    '''
    Takes any method with adequeste url, token, payload.
    Runs API call based on parameters.
    Returns json object.
    '''

    headers = {
    'Content-Type': content_type,
    'Authorization': 'Bearer {}'.format(token)
    }

    response = requests.request(method, url, headers=headers, data=payload)
    print("Response Status: {} \n".format(response))
    
    return json.loads(response.text)