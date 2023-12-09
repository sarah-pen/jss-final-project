import requests
import json
import os
import re
import sqlite3
from bs4 import BeautifulSoup
import time


key = "A3phA47g5rC6uF9zpmgWGxlD7SCtsimG"
database = "tour_shows.db"

def get_url(root, artist):
    full_url = root + "apikey=" + key + "&keyword=" + artist
    return full_url


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
    

def write_json(filename, dict):
    '''
    Encodes dict into JSON format and writes
    the JSON to filename to save the search results
    '''

    with open(filename, 'w') as file:
        file.truncate()
        file.write(json.dumps(dict))
        file.close()


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
    while True:
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

    for k in data:
        events = data[k]["events"]
        lst = []

        for event in events:
            inner_d = {}
            name = event["name"]
            date = event["dates"]["start"]["localDate"]
            if "_embedded" in event:
                city = event["_embedded"]["venues"][0]["city"]["name"]
                artist = event["_embedded"]["attractions"][0]["name"]
                # venue_url = event["_embedded"]["venues"][0]["url"]
                # r = requests.get(venue_url)
                # soup = BeautifulSoup(r.content, 'html.parser')
                # venue_name = soup.find('h1', class_='sc-lmu4mw-6').text
                # inner_d["venue"] = venue_name

            else:
                break

            inner_d["city"] = city
            inner_d["artist"] = artist
            inner_d["date"] = date

            if "priceRanges" in event:
                min_price = event["priceRanges"][0]["min"]
                max_price = event["priceRanges"][0]["max"] 
            else:
                break

            if "_links" in event:
                # time.sleep(5)
                venue_link = event["_links"]["venues"][0]["href"]
                link = re.findall(".*\?", venue_link)[0]
                full_venue = "https://app.ticketmaster.com" + link + "&apikey=" + key
                venue_resp = requests.get(full_venue).json()
                venue_name = venue_resp.get("name", "Error")
                inner_d["venue"] = venue_name

            inner_d["min_price"] = min_price
            inner_d["max_price"] = max_price
            lst.append(inner_d)

            events_d[name] = lst

    print(events_d["Taylor Swift | The Eras Tour"])
    return events_d

def insert_data(dict):
    
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS Events')
    cur.execute('CREATE TABLE IF NOT EXISTS Events (show_id INTEGER PRIMARY KEY, artist TEXT, name TEXT, city TEXT, venue TEXT, date TEXT, min_price INTEGER, max_price INTEGER)')
    cur.execute('CREATE TABLE IF NOT EXISTS Cities (city_id INTEGER PRIMARY KEY, name TEXT UNIQUE)')

    # id = 0

    for name, shows in dict.items():

        # if id != 0 and id % 25 == 0:
        #     break

        # cur.execute("SELECT COUNT(*) FROM Events")
        # id = cur.fetchone()

        for show in shows:
            city = show["city"]
            artist = show["artist"]
            cur.execute('INSERT OR IGNORE INTO Cities (city_id, name) VALUES (NULL, ?)', (city,))
            venue = show["venue"]
            date = show["date"]
            min_price = show["min_price"]
            max_price = show["max_price"]
            cur.execute('INSERT OR IGNORE INTO Events (show_id, artist, name, city, venue, date, min_price, max_price) VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)', (name, artist, city, venue, date, min_price, max_price))
            # id += 1

    conn.commit()
    conn.close()
    


def main():

    root = "https://app.ticketmaster.com/discovery/v2/events.json?"

    url = get_url(root, "Taylor_Swift")
    cache_all_pages(url, "events.json")
    events = event_info("events.json")
    # print(events)
    insert_data(events)
    

if __name__ == "__main__":
    main()

