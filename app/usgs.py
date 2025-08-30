import os
import requests
import json
import datetime
import xmltodict

def process_data(data):
    output = []
    for rec in data:
        type_ = rec['type']
        if type_ != 'earthquake':
            pass
        else:
            id_ = rec['origin']['@catalog:dataid']
            location = rec['description']['text'].split("of ")[-1]
            mag = rec['magnitude']['mag']['value']
            depth =  rec['origin']['depth']['value']
            time = rec['origin']['time']['value']
            
            output.append({
                "id":id_,
                "location": location,
                "mag":mag,
                "depth":depth,
                "time":time
            })
        
        
    return output

def fetch_usgs():
    
    # Setting today as reference day for api extraction
    start_time = datetime.date.today() 
    url = f'https://earthquake.usgs.gov/fdsnws/event/1/query?format=xml&starttime={start_time}'

    request = requests.get(url)

    # Validating sucessful API request
    if str(request.status_code)[0] == '2':

        request = requests.get(url).text
        data = xmltodict.parse(request)['q:quakeml']['eventParameters']['event']

        # Keeping only relevant fields
        data = process_data(data)
        
        # Logging registered records
        print(f"Fetched {len(data)} earthquake records since {start_time}")
        return data
    
    else:
        raise Exception('Invalid API Request to USGS')
        
        
