import requests
import json
import time

def submitMediaUpdate(config, embyChanges):
    embyApiBaseUrl = config['protocol'] + '://' + config['ip'] + ':' + config['port'] + '/emby/'
    mediaUpdatePath = 'Library/Media/Updated'
    requestUrl = embyApiBaseUrl + mediaUpdatePath
    params = {'api_key' : config['apiKey']}

    retries = config['retries']
    retryCount = 0
    try:
        r = requests.post(url = requestUrl, params = params, json = embyChanges)
        print(f'Request body sent to Emby: {r.request.body}')
        r.raise_for_status()
        print(f"Sent {len(embyChanges.get('Updates'))} emby changes successfully")
        return True
    except Exception as exc:
        print(f'Issue while trying to send reques to Emby. Error: {exc}')
        if(retryCount < retries):
            retryCount += 1
            print(f'Trying again, retry # {retryCount}')
            time.sleep(1)
            submitMediaUpdate(config, embyChanges)
        else:
            print(f'Unable to submit request to Emby after retries')
            return False