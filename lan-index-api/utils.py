import requests
from time import sleep

def getMacManufacturer(mac):
    try:
        r = requests.get(f'https://api.maclookup.app/v2/macs/{mac}')
        sleep(1)
        resp = r.json()
        if resp['success'] and resp['found']:
            return resp['company']
        else:
            return 'Unknown'    
    except:
        return 'Unknown'