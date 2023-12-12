import requests
import sqlite3

api_key = "28057900aa8badddae0f85dbdfb8848b"
username = "Sarah297"
base_url = 'http://ws.audioscrobbler.com/2.0/'
database = 'music.db'
# database = 'test.db'

def delete_artists_table():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS Artists')
    conn.commit()
    conn.close()


def insert_data_into_table(artist_list):
    '''
    INSERTS ARTIST DATA!
    artist_list is of the form {'artist': artist_name, 'plays': plays}
    '''
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    # cursor.execute('CREATE TABLE IF NOT EXISTS Artists (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)')
    cursor.execute('CREATE TABLE IF NOT EXISTS Artists (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, plays INTEGER)')
    # count = 1
    # Iterate over tracks and insert artists into the table
    for item in artist_list:
        artist = item['artist']
        plays = int(item['plays'])
        # Use INSERT OR IGNORE to insert only if the artist doesn't exist
        cursor.execute('INSERT OR IGNORE INTO Artists (name, plays) VALUES (?, ?)', (artist, plays))
        print(f"Inserted {artist} with {plays} plays or artist already in table")


    conn.commit()
    conn.close()


def get_username():
    user = input("What is your last.fm username?")
    username = user

def get_top_songs(api_key, username, period='overall', limit=10):
    params = {
        'method': 'user.getTopTracks',
        'user': username,
        'api_key': api_key,
        'format': 'json',
        'limit': limit
    }
    response = requests.get(base_url, params=params)
    data = response.json()['toptracks']['track']
    songs_list = []
    for item in data:
        song_name = item['name']
        artist_name = item['artist']['name']
        playcount = item['playcount']
        songs_list.append({'artist': artist_name, "track": song_name, "plays": playcount})
    return songs_list

def add_songs_to_database(api_key, database, tracks_list):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS Songs (artist_id INTEGER PRIMARY KEY, name TEXT UNIQUE, plays INTEGER)')
    # tracks_list.append({'track': 'Placeholder Obscure Song', 'artist': 'QWERTY', 'plays': 3})
    for item in tracks_list:
        track = item['track']
        artist = item['artist']
        plays = item['plays']
        cursor.execute("SELECT id FROM Artists WHERE name=?", (artist,))
        id = cursor.fetchall()
        try:
            id = id[0][0]
        except:
            # Artist not yet in DB
            cursor.execute('INSERT OR IGNORE INTO Artists (name, plays) VALUES (?, ?)', (artist, plays))
            cursor.execute("SELECT id FROM Artists WHERE name=?", (artist,))
            id = cursor.fetchall()[0][0]
        # print(f"integer id for {artist} is {id}")
        cursor.execute('INSERT OR IGNORE INTO Songs (artist_id, name, plays) VALUES (?, ?, ?)', (id, track, plays))
        print(f"inserted or ignored {track} by {artist}")
    conn.commit()
    conn.close()


def get_top_artists(api_key, username, period='overall', limit=5, page=1):

    params = {
        'method': 'user.getTopArtists',
        'user': username,
        'period': period,
        'page': page,
        'limit': limit,
        'api_key': api_key,
        'format': 'json'
    }
    num_results = limit * page

    response = requests.get(base_url, params=params)
    data = response.json()

    artists_list = []

    # print(data)

    # for i in range(num_results):
    #     artist = data['topartists']['artist'][i]
    #     artist_name = artist['name']
    #     plays = int(artist['playcount'])
    #     # print(f"{i+1}) {artist_name} - {plays} plays")
    #     data = artists_list.append({'artist': artist_name, 'plays': plays})

    for artist in data['topartists']['artist']:
        artist_name = artist['name']
        plays = int(artist['playcount'])
        # print(f"{artist_name} - {plays} plays")
        data = artists_list.append({'artist': artist_name, 'plays': plays})

    return artists_list

def get_recent_plays(api_key, username, limit=50, page=1):
    base_url = 'http://ws.audioscrobbler.com/2.0/'

    params = {
        'method': 'user.getRecentTracks',
        'user': username,
        'limit': limit,
        'api_key': api_key,
        'format': 'json',
        'page' : page,
        'extended': 0
    }

    response = requests.get(base_url, params=params)
    data = response.json()['recenttracks']['track'] # this is a list
    tracks_list = []
    for track in data: # track is a dictionary
        artist_name = track['artist']['#text']
        track_name = track['name']
        album_name = track['album']['#text']
        # print(f"{artist_name}: {track_name} on {album_name}")
        tracks_list.append({'artist': artist_name, 'track': track_name, 'album': album_name})
    return tracks_list


def main():
    # delete_artists_table()
    # data = get_top_artists(api_key, username, period="overall", limit=50)
    # insert_data_into_table(data)
    # data = get_recent_plays(api_key, username, limit=100)
    # insert_data_into_table(data)
    # lsit = get_top_songs(api_key, username, limit=20)
    # add_songs_to_database(api_key, database, lsit)
    pass


if __name__ == "__main__":
    main()
