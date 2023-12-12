# Completed by Sarah Penrose

import requests
import json
import os
import re
import sqlite3


key = "A3phA47g5rC6uF9zpmgWGxlD7SCtsimG"

def get_artists(conn, cur):
    cur.execute('SELECT * FROM Artists')
    artists = cur.fetchall()
    lst = []
    for artist in artists:
        lst.append(artist[0])
    conn.commit()
    conn.close()
    return lst

key = "6QRG2uyfHy57J8Ck7nnTSAiiGtzxo2CG"
database = "music.db"

def get_url(root, artist):
    full_url = root + "apikey=" + key + "&keyword=" + artist
    return full_url


def get_data(url):

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

    dct = load_json(filename)
    root_url = url

    # if first page of retrieved data is not in dictionary, empty the dictionary
    if get_data(url)["_embedded"] != dct["page 0"]:
        dct = {}
        page_num = 0

    # if not, pick up where you left off
    else:
        page_num = int(list(dct.keys())[-1][-1])

    while True:
        # data returned by url
        info = get_data(url)
        # if data is fruitful
        if "_embedded" in info:
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

    # loop through pages
    for k in data:
        events = data[k]["events"]

        # loop through events
        for event in events:
            inner_d = {}
            # name = event["name"]
            date = event["dates"]["start"]["localDate"]
            if "_embedded" in event:
                city = event["_embedded"]["venues"][0]["city"]["name"]
                artist = event["_embedded"]["attractions"][0]["name"]

                inner_d["city"] = city
                # inner_d["artist"] = artist
                inner_d["date"] = date

            else:
                pass

            if "priceRanges" in event:
                min_price = event["priceRanges"][0]["min"]
                max_price = event["priceRanges"][0]["max"]
                inner_d["min_price"] = min_price
                inner_d["max_price"] = max_price
            else:
                pass

            if "venues" in event["_links"]:
                venue_link = event["_links"]["venues"][0]["href"]
                link = re.findall(".*\?", venue_link)[0]
                full_venue = "https://app.ticketmaster.com" + link + "&apikey=" + key
                venue_resp = requests.get(full_venue).json()
                venue_name = venue_resp.get("name", "Error")
                inner_d["venue"] = venue_name
            else:
                continue

            if artist not in events_d:
                events_d[artist] = [inner_d]
            else:
                events_d[artist].append(inner_d)

    return events_d

def insert_data(conn, cur, artists):

    cur.execute('DROP TABLE IF EXISTS Events')
    cur.execute('CREATE TABLE IF NOT EXISTS Events (show_id INTEGER PRIMARY KEY, artist TEXT, city TEXT, venue TEXT, date TEXT UNIQUE, min_price INTEGER, max_price INTEGER)')
    cur.execute('DROP TABLE IF EXISTS Touring_Artists')
    cur.execute('CREATE TABLE IF NOT EXISTS Touring_Artists (artist_id INTEGER PRIMARY KEY, name TEXT UNIQUE)')
    cur.execute('CREATE TABLE IF NOT EXISTS Cities (city_id INTEGER PRIMARY KEY, name TEXT UNIQUE)')
    cur.execute('CREATE TABLE IF NOT EXISTS Venues (venue_id INTEGER PRIMARY KEY, name TEXT UNIQUE)')


    root = "https://app.ticketmaster.com/discovery/v2/events.json?"

    # get initial table size
    cur.execute("SELECT COUNT(*) FROM Events")
    table_size = cur.fetchone()[0]

    if table_size >= 150:
            print("You don't need to add anything more!")
            pass

    # if table is not at 150 rows...
    else:

        # loop through passed in artists
        for artist in artists:
            artist = artist.split(" ")
            artist = "_".join(artist)
            url = get_url(root, artist)
            cache_all_pages(url, "events.json")
            events = event_info("events.json")

            # loop through artist dictionary
            for name, shows in events.items():
                # loop through their shows
                for show in shows:

                    # get current size of table
                    cur.execute("SELECT COUNT(*) FROM Events")
                    current_size = cur.fetchone()[0]
                    print(current_size)

                    # if 25 items have been added, exit
                    if current_size == (table_size + 25):
                        break

                    city = show["city"]
                    artist = name
                    venue = show.get("venue", None)
                    date = show["date"]
                    min_price = show.get("min_price", None)
                    max_price = show.get("max_price", None)

                    # if row has already been added, move on to the next one
                    cur.execute('SELECT * FROM Events WHERE artist=? AND city=? AND venue=? AND date=? AND min_price=? AND max_price=?', (artist, city, venue, date, min_price, max_price))
                    if len(cur.fetchall()) == 1:
                        continue
                    # insert data
                    cur.execute('INSERT OR IGNORE INTO Events (show_id, artist, city, venue, date, min_price, max_price) VALUES (NULL, ?, ?, ?, ?, ?, ?)', (artist, city, venue, date, min_price, max_price))
                    cur.execute('INSERT OR IGNORE INTO Touring_Artists (artist_id, name) VALUES (NULL, ?)', (artist,))
                    cur.execute('INSERT OR IGNORE INTO Cities (city_id, name) VALUES (NULL, ?)', (city,))
                    cur.execute('INSERT OR IGNORE INTO Venues (venue_id, name) VALUES (NULL, ?)', (venue,))
                break

    conn.commit()
    conn.close()


def join_tables(conn, cur):

    cur.execute('SELECT COUNT(*) FROM Events')
    size = cur.fetchall()[0]
    if size == (150,):
        cur.execute('CREATE TABLE Events_Final AS SELECT Events.show_id, Touring_Artists.artist_id, Cities.city_id, Venues.venue_id, Events.date, Events.min_price, Events.max_price FROM Events JOIN Touring_Artists ON Events.artist=Touring_Artists.name JOIN Cities ON Events.city=Cities.name JOIN Venues ON Events.venue=Venues.name')
    else:
        pass

    conn.commit()
    conn.close()



def main():

    conn = sqlite3.connect("music.db")
    cur = conn.cursor()

    # artists = ["Noah Kahan", "Taylor Swift", "Niall Horan", "Zach Bryan", "Chelsea Cutler", "Mitski", "Laufey"]

    get_artists(conn, cur)
    insert_data(conn, cur, artists)
    join_tables(conn, cur)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
