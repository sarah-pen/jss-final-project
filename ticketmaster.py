# Completed by Sarah Penrose

import requests
import json
import os
import re
import sqlite3

key = "i9XlPBAqEYI2MnQEqTIonXthBZNQBSN7"
database = "music.db"

# -----------------------------------------------------------

def get_artists(conn, cur):
    '''
    Retrieves artists from LastFM table and returns them in a list
    '''
    cur.execute('SELECT * FROM Artists')
    artists = cur.fetchall()
    lst = []
    for artist in artists:
        lst.append(artist[0])
    conn.commit()
    return lst


def get_url(root, artist):
    '''
    Takes the root url and artist name and returns the full url
    '''
    full_url = root + "apikey=" + key + "&keyword=" + artist
    return full_url


def get_data(url):
    '''
    Retrieves data from passed in URL
    '''
    
    try:
        resp = requests.get(url)
        data = resp.json()
        return data
    except:
        return "Exception!"


def write_json(filename, dict):
    '''
    Encodes dict into JSON format and writes
    the JSON to filename to save the results
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
    Saves all pages to the JSON file, with page numbers as the keys
    '''

    dct = load_json(filename)
    root_url = url

    if "_embedded" in get_data(url):
        # if first page of retrieved data is not in dictionary, empty the dictionary
        if (len(dct) == 0) or (get_data(url)["_embedded"] != dct["page 0"]):
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
    elif len(dct) > 0:
        return "No data"
    else:
        return "No data"


def event_info(filename):
    '''
    Takes in the JSON dictionary (with all pages) and returns a simplified dictionary with the artist name
    as the key and event details as the values
    '''

    data = load_json(filename)
    if len(data) <= 2:
        return None
    
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
                if "venues" in event["_embedded"]:
                    city = event["_embedded"]["venues"][0]["city"]["name"]
                else:
                    city = None
                if "attractions" in event["_embedded"]:
                    artist = event["_embedded"]["attractions"][0]["name"]
                else:
                    artist = None

                inner_d["city"] = city
                # inner_d["artist"] = artist
                inner_d["date"] = date

            else:
                pass

            if "priceRanges" in event:
                min_price = event["priceRanges"][0].get("min", None)
                max_price = event["priceRanges"][0].get("max", None)
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
    '''
    Writes data to a SQLite database
    '''

    # cur.execute('DROP TABLE IF EXISTS Events')
    cur.execute('CREATE TABLE IF NOT EXISTS Events (show_id INTEGER PRIMARY KEY, artist TEXT, city TEXT, venue TEXT, date TEXT UNIQUE, min_price INTEGER, max_price INTEGER)')
    # cur.execute('DROP TABLE IF EXISTS Touring_Artists')
    cur.execute('CREATE TABLE IF NOT EXISTS Touring_Artists (artist_id INTEGER PRIMARY KEY, name TEXT UNIQUE)')
    # cur.execute('DROP TABLE IF EXISTS Cities')
    cur.execute('CREATE TABLE IF NOT EXISTS Cities (city_id INTEGER PRIMARY KEY, name TEXT UNIQUE)')
    # cur.execute('DROP TABLE IF EXISTS Venues')
    cur.execute('CREATE TABLE IF NOT EXISTS Venues (venue_id INTEGER PRIMARY KEY, name TEXT UNIQUE)')


    root = "https://app.ticketmaster.com/discovery/v2/events.json?"

    # get initial table size
    cur.execute("SELECT COUNT(*) FROM Events")
    table_size = cur.fetchone()[0]

    if table_size >= 120:
            print("You don't need to add anything more!")
            pass

    # if table is not at 150 rows...
    else:

        # loop through passed in artists
        for artist in artists:
            artist_name = artist.split(" ")
            artist_name = "_".join(artist_name)
            url = get_url(root, artist_name)
            cache_all_pages(url, "events.json")
            events = event_info("events.json")
            if events == None:
                continue
            # loop through artist dictionary
            for name, shows in events.items():
                # loop through their shows
                for show in shows:

                    # get current size of table
                    cur.execute("SELECT COUNT(*) FROM Events")
                    current_size = cur.fetchone()[0]
                    # print("Current table size: " + str(current_size))


                    # if 25 items have been added, exit
                    if current_size == (table_size + 25):
                        break

                    city = show["city"]
                    # artist = name
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

                    cur.execute("SELECT COUNT(*) FROM Events")
                    current_size = cur.fetchone()[0]
                    print("Current table size: " + str(current_size))
                break
            
            if current_size == (table_size + 25):
                break
            else:
                continue

    conn.commit()


def join_tables(conn, cur):
    '''
    Joins main table with other tables (venues, cities, artists) to avoid duplicate string data
    '''
    # cur.execute('DROP TABLE IF EXISTS Events_Final')
    cur.execute('SELECT COUNT(*) FROM Events')
    size = cur.fetchall()[0]
    if size == (129,):
        cur.execute('CREATE TABLE Events_Final AS SELECT Events.show_id, Touring_Artists.artist_id, Cities.city_id, Venues.venue_id, Events.date, Events.min_price, Events.max_price FROM Events JOIN Touring_Artists ON Events.artist=Touring_Artists.name JOIN Cities ON Events.city=Cities.name JOIN Venues ON Events.venue=Venues.name')
    else:
        pass

    conn.commit()


# ---- Main function ----

def main():

    conn = sqlite3.connect("music.db")
    cur = conn.cursor()

    artists = get_artists(conn, cur)
    insert_data(conn, cur, artists)
    join_tables(conn, cur)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
