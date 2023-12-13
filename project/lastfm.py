import requests
import sqlite3

api_key = "81afb2d4a16555a6d6e469c9294a3344"
username = "Sarah297"
base_url = 'http://ws.audioscrobbler.com/2.0/'
database = 'music.db'
# database = 'test.db'

class Counter:
    def __init__(self):
      self.artists = 0
      self.songs = 0

def get_and_insert_top_artists(database, counter, period='alltime', limit='125'):
    params = {
        'method': 'user.getTopArtists',
        'user': username,
        'period': period,
        'limit': limit,
        'api_key': api_key,
        'format': 'json'
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    conn = sqlite3.connect(database)
    cursor = conn.cursor()


    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Artists (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        rating INTEGER NOT NULL DEFAULT 0,
                        country_id INTEGER DEFAULT NULL,
                        plays INTEGER NOT NULL,
                        FOREIGN KEY (country_id) REFERENCES Countries(id)
                   )
                   ''')
    for artist in data['topartists']['artist']:
        artist_name = artist['name']
        plays = int(artist['playcount'])

        cursor.execute('INSERT OR IGNORE INTO Artists (name, plays) VALUES (?, ?)', (artist_name, plays))
        # Check if anything was inserted
        if cursor.rowcount > 0:
            print(f"Artist {artist_name} was inserted")
            counter.artists += 1
        else:
            print(f"Artist {artist_name} was already in the table")

        if counter.artists >= 25:
            break

    conn.commit()
    conn.close()
    return

def get_and_insert_top_songs(database, counter, period='alltime', limit='125'):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    params = {
        'method': 'user.getTopTracks',
        'user': username,
        'api_key': api_key,
        'format': 'json',
        'limit': limit
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Songs (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  artist_id INTEGER NOT NULL,
                  name TEXT UNIQUE NOT NULL,
                  plays INTEGER,
                  FOREIGN KEY (artist_id) REFERENCES Artists(id)
                  )''')

    for item in data['toptracks']['track']:
        song_name = item['name']
        artist_name = item['artist']['name']
        playcount = item['playcount']

        cursor.execute("SELECT id FROM Artists WHERE name=?", (artist_name,))
        id = cursor.fetchall()

        try:
            id = id[0][0]
        except:
            # Artist not yet in DB
            if counter.artists >= 25:
                continue
            else:
              cursor.execute('INSERT OR IGNORE INTO Artists (name, plays) VALUES (?, ?)', (artist_name, playcount))
              cursor.execute("SELECT id FROM Artists WHERE name=?", (artist_name,))
              counter.artists += 1
              id = cursor.fetchall()[0][0]

        cursor.execute('INSERT OR IGNORE INTO Songs (artist_id, name, plays) VALUES (?, ?, ?)', (id, song_name, playcount))
        if cursor.rowcount > 0:
            print(f"Song {song_name} was inserted")
            counter.songs += 1
        else:
            print(f"Song {song_name} was already in the table")
        if counter.songs >= 25:
            break

    conn.commit()
    conn.close()
    return

def main():
    counter = Counter()
    get_and_insert_top_artists(database, counter)
    get_and_insert_top_songs(database, counter)

if __name__ == "__main__":
    main()
