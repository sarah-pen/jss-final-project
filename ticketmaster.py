import requests
import json
import os

# root URL : https://app.ticketmaster.com/{package}/{version}/{resource}.json?apikey=**{API key}


def get_data(api_key, page):
    '''
    Check whether the 'params' dictionary has been specified. 
    Makes a request to access data with the 'url' and 'params' given, if any. 
    If the request is successful, return a dictionary representation 
    of the decoded JSON. If the search is unsuccessful, print out "Exception!"
    and return None.
    '''

    # https://app.ticketmaster.com/discovery/v2/events.json?apikey=A3phA47g5rC6uF9zpmgWGxlD7SCtsimG&keyword=Taylor%20Swift
    
    resp = requests.get("https://app.ticketmaster.com/discovery/v2/events.json", params={"apikey": api_key, "attractionId": "K8vZ9175Tr0", "page": page})
    data = resp.json()
    return data

    
def write_json(filename, dict):
    '''
    Encodes dict into JSON format and writes
    the JSON to filename to save the search results
    '''

    f = open(filename, "w")
    f.write(json.dumps(dict))
    f.close()


def load_json(filename):

    '''
    Loads a JSON cache from filename if it exists and returns dictionary
    with JSON data or an empty dictionary if the cache does not exist
    '''

    try:
        source_dir = os.path.dirname(__file__)
        full_path = os.path.join(source_dir, filename)

        f = open(full_path)
        contents = f.read()
        f.close()

        data = json.loads(contents)

        return data
    
    except:
        return {}
    

def cache_all_pages(url, filename):
    '''
    1. Checks if the page number is found in the dict return by `load_json`
    2. If the page number does not exist in the dictionary, it makes a request (using get_swapi_info)
    3. Add the data to the dictionary (the key is the page number (Ex: page 1) and the value is the results).
    4. Write out the dictionary to a file using write_json.
    '''
    pass

def event_info(filename):

    # dct = json.loads(resp.content)
    # events = dct["_embedded"]["events"]

    # for event in events:
    #     city = event["_embedded"]["venues"][0]["city"]["name"]

    #     if "priceRanges" in event:
    #         max_price = str(event["priceRanges"][0]["max"])
    #         print(city + ": max " + max_price)
    #     else:
    #         print(city + ": none")
    pass

    


def main():

    data = get_data("A3phA47g5rC6uF9zpmgWGxlD7SCtsimG", 2)
    write_json("test.json", data)


if __name__ == "__main__":
    main()

