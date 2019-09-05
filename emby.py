import requests
import json

def submitMediaUpdate(config, embyChanges):
    embyApiBaseUrl = config['protocol'] + '://' + config['ip'] + ':' + config['port'] + '/emby/'
    mediaUpdatePath = 'Library/Media/Updated'
    requestUrl = embyApiBaseUrl + mediaUpdatePath
    params = {'api_key' : config['apiKey']}

    r = requests.post(url = requestUrl, params = params, json = embyChanges)
    print(f'Request body sent to Emby: {r.request.body}')

    try:
        r.raise_for_status()
        print(f"Sent {len(embyChanges.get('Updates'))} emby changes successfully")
    except requests.exceptions.HTTPError as e:
        raise e