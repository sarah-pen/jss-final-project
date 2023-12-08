import requests
import json
import os

# root URL : https://app.ticketmaster.com/{package}/{version}/{resource}.json?apikey=**{API key}


def get_url(root, apikey, artist):

    full_url = root + "apikey=" + apikey + "&keyword=" + artist
    return full_url

# DONE
def get_data(url):
    '''
    Check whether the 'params' dictionary has been specified. 
    Makes a request to access data with the 'url' and 'params' given, if any. 
    If the request is successful, return a dictionary representation 
    of the decoded JSON. If the search is unsuccessful, print out "Exception!"
    and return None.
    '''

    # https://app.ticketmaster.com/discovery/v2/events.json?apikey=A3phA47g5rC6uF9zpmgWGxlD7SCtsimG&keyword=Taylor%20Swift
    
    try:
        resp = requests.get(url)
        data = resp.json()
        return data
    
    except:
        return "Exception!"

    
# DONE
def write_json(filename, dict):
    '''
    Encodes dict into JSON format and writes
    the JSON to filename to save the search results
    '''

    f = open(filename, "w")
    f.write(json.dumps(dict))
    f.close()


# DONE
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
    2. If the page number does not exist in the dictionary, it makes a request (using get_data)
    3. Add the data to the dictionary (the key is the page number and the value is the results).
    4. Write out the dictionary to a file using write_json.
    '''

    dct = load_json(filename)

    page_num = 0
    root_url = url

    # while page isn't in dictionary yet
    while page_num not in dct:

        # data returned by url
        info = get_data(url)

        # if data is fruitful
        if info != None:

            # add data from "results" key to dictionary
            dct["page " + str(page_num)] = info["_embedded"]
            # if page isn't the last one
            if "next" in info["_links"]:
                # save "next" value as new url
                page_num += 1
                url = root_url + "&page=" + str(page_num)
                # proceed to next page
            else:
                break
        else:
            break

    write_json(filename, dct)


def event_info(filename):

    data = load_json(filename)
    events_d = {}

    for d in data.values():
        
        events = d["events"]
        
        for event in events:

            lst = []
            inner_d = {}
            name = event["name"]

            if "_embedded" in event:
                # venue = event["_embedded"]["venues"][0]["name"]
                city = event["_embedded"]["venues"][0]["city"]["name"]
                artist = event["_embedded"]["attractions"][0]["name"]
            
            else:
                city = "No city given"
                artist = "No artist given"

            # inner_d["venue"] = venue
            inner_d["city"] = city
            inner_d["artist"] = artist

            if "priceRanges" in event:
                min_price = event["priceRanges"][0]["min"]
                max_price = event["priceRanges"][0]["max"]
                
            else:
                min_price = "No price data"
                max_price = "No price data"

            inner_d["min_price"] = min_price
            inner_d["max_price"] = max_price
            lst.append(inner_d)

            events_d[name] = lst

    print(events_d)
    return events_d




def main():

    root = "https://app.ticketmaster.com/discovery/v2/events.json?"
    key = "A3phA47g5rC6uF9zpmgWGxlD7SCtsimG"

    url = get_url(root, key, "Taylor_Swift")

    cache_all_pages(url, "events.json")
    event_info("events.json")
    

if __name__ == "__main__":
    main()

