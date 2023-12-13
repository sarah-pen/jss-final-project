# Completed by Sarah Penrose

import requests
import json
import os
import re
import sqlite3

key = "xWeTlRn2AItFvhGrkcjJGGQueAYGqWJy"
database = "music.db"

# -----------------------------------------------------------

def get_artists(conn, cur):
    '''
    Retrieves artists from Artists table and returns them in a list
    '''
    cur.execute('SELECT name FROM Artists')
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
    Retrieves data from passed in URL and returns it
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

    elif len(dct) == 0:
        write_json(filename, dct)
        return "No data"
    else:
        write_json(filename, dct)
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
            date = event["dates"]["start"]["localDate"]
            if "_embedded" in event:
                try:
                    city = event["_embedded"]["venues"][0]["city"]["name"]
                except:
                    city = None
                try:
                    artist = event["_embedded"]["attractions"][0]["name"]
                except:
                    artist = event["name"]

            else:
                city = None
                artist = event["name"]
                date = None

            inner_d["city"] = city
            inner_d["date"] = date

            if "priceRanges" in event:
                min_price = event["priceRanges"][0].get("min", None)
                max_price = event["priceRanges"][0].get("max", None)
                inner_d["min_price"] = min_price
                inner_d["max_price"] = max_price
            else:
                pass

            if (city == None) and (date == None):
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

    cur.execute('''
                CREATE TABLE IF NOT EXISTS Cities (
                    id          INTEGER     NOT NULL PRIMARY KEY     AUTOINCREMENT,
                    name        TEXT        NOT NULL UNIQUE
                )
                ''')
    cur.execute('''
                CREATE TABLE IF NOT EXISTS Events (
                    show_id     INTEGER     PRIMARY KEY,
                    artist_id   INTEGER     NOT NULL,
                    city_id     INTEGER     NOT NULL,
                    date        TEXT        NOT NULL UNIQUE,
                    min_price   INTEGER,
                    max_price   INTEGER
                )
                ''')


    root = "https://app.ticketmaster.com/discovery/v2/events.json?"

    # get initial table size
    cur.execute("SELECT COUNT(*) FROM Events")
    table_size = cur.fetchone()[0]

    if table_size >= 250:
        print("You don't need to add anything more!")
        pass
    else:
        for artist in artists:
            artist_name = artist.split(" ")
            artist_name = "_".join(artist_name)
            url = get_url(root, artist_name)
            cache_all_pages(url, "events.json")
            events = event_info("events.json")
            if events == None:
                continue
            # loop through artist dictionary
            for shows in events.values():

                # show_id = 1
                # loop through their shows
                for show in shows:

                    # get current size of table
                    cur.execute("SELECT COUNT(*) FROM Events")
                    current_size = cur.fetchone()[0]

                    # if 25 items have been added, exit
                    if current_size == (table_size + 25):
                        break

                    city_name = show.get("city")
                    cur.execute('''
                                INSERT OR IGNORE INTO Cities
                                (name)
                                VALUES (?)
                                ''',
                                (city_name,))
                    cur.execute('''
                                SELECT id
                                FROM Cities
                                WHERE name = ?
                                ''',
                                (city_name,))

                    city_id = cur.fetchone()[0]

                    date = show.get("date", None)
                    min_price = show.get("min_price", None)
                    max_price = show.get("max_price", None)

                    cur.execute('''
                                INSERT OR IGNORE INTO Events
                                (artist_id, city_id, date, min_price, max_price)
                                VALUES ((SELECT id FROM Artists WHERE name = ?), ?, ?, ?, ?)
                                ''',
                                (artist, city_id, date, min_price, max_price))

                    cur.execute("SELECT COUNT(*) FROM Events")
                    current_size = cur.fetchone()[0]
                    print("Current table size: " + str(current_size))
                break

            if current_size == (table_size + 25):
                break
            else:
                continue

    conn.commit()


# ---- Main function ----

def main():

    conn = sqlite3.connect("music.db")
    cur = conn.cursor()

    artists = get_artists(conn, cur)
    insert_data(conn, cur, artists)

    cur.execute('SELECT * FROM Events')
    events = cur.fetchall()
    for event in events:
        artist = event[1]
        city = event[2]
        date = event[3]
        min_price = event[4]
        max_price = event[5]
        print(f"{artist} performing in {city} on {date}. Min price is {min_price} and max price is {max_price}.")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
