import requests
import sqlite3

api_key = "28057900aa8badddae0f85dbdfb8848b"
username = "Sarah297"
base_url = 'http://ws.audioscrobbler.com/2.0/'
database = 'music.db'


def insert_data_into_table(tracks_list):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS Artists (name TEXT)')
    print("inserting artists...")
    for item in tracks_list:
        artist = item['artist']
        cursor.execute('SELECT name FROM Artists WHERE name = ?', (artist,))
        existing_artist = cursor.fetchone()
        if not existing_artist:
            cursor.execute('INSERT INTO Artists (name) VALUES (?)', (artist,))
            print(f"Inserted {artist}")
        else:
            print(f"Artist {artist} already in table")

    conn.commit()
    conn.close()


def get_username():
    user = input("What is your last.fm username?")
    username = user

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

    pass


def main():
    data = get_top_artists(api_key, username, period="overall", limit=25)
    insert_data_into_table(data)
    data = get_recent_plays(api_key, username, limit=50)
    insert_data_into_table(data)
    pass


if __name__ == "__main__":
    main()
