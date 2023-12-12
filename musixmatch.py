import requests
import sqlite3
import json
import matplotlib.pyplot as plt

api_key = "4ced0fe04de2090cb8f068ca309e8d96"
base_url = "https://api.musixmatch.com/ws/1.1/"
database = 'music.db'

#inserts or updates the artist's rating.
def add_rating(artist_name, rating, database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS Ratings (artist TEXT PRIMARY KEY, rating INTEGER)')
    cursor.execute('INSERT OR REPLACE INTO Ratings (artist, rating) VALUES (?, ?)', (artist_name, rating))
    conn.commit()
    conn.close()

def add_artist_country(artist_name, country, database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS ArtistCountry (artist TEXT PRIMARY KEY, country TEXT)')
    cursor.execute('INSERT OR REPLACE INTO ArtistCountry (artist, country) VALUES (?, ?)', (artist_name, country))
    conn.commit()
    conn.close()

#inserts or updates artist/song genre
#def add_song_genre(artist_name, song_name, genre, database):
    #conn = sqlite3.connect(database)
    #cursor = conn.cursor()
    #cursor.execute("CREATE TABLE IF NOT EXISTS SongGenres (artist TEXT, song TEXT, genre TEXT, PRIMARY KEY (artist, song))")
    #cursor.execute("INSERT OR REPLACE INTO SongGenres (artist, song, genre) VALUES (?, ?, ?)", (artist_name, song_name, genre))
    #conn.commit()
    #conn.close()

#retrieves a list of artist names from the SQLite database.
def get_artists_from_db(database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Artists")
    artists = cursor.fetchall()
    conn.close()
    artist_names = [artist[0] for artist in artists]
    return artist_names

#retrieves list of artist names and songs from database
#def get_artists_and_songs(database):
    #conn = sqlite3.connect(database)
   # cursor = conn.cursor()
    #cursor.execute("SELECT name, song FROM Artists")
    #data = cursor.fetchall()
    #conn.close()
   # return data

#fetch the artist's rating from the Musixmatch API
def get_artist_rating_from_musixmatch(artist_name, api_key):
    base_url_musixmatch = 'https://api.musixmatch.com/ws/1.1/'
    method = 'artist.search'
    url = base_url_musixmatch + method
    params = {
        'q_artist': artist_name,
        'apikey': api_key,
        'format': 'json'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        artist_list = data.get("message", {}).get("body", {}).get("artist_list", [])
        if artist_list:
            artist = artist_list[0].get("artist", {})
            artist_rating = artist.get("artist_rating", None)
            if artist_rating is not None:
                add_rating(artist_name, artist_rating, database)
            return artist_rating
    return "Error or artist not found"

def get_artist_country_from_musixmatch(artist_name, api_key, database):
    base_url_musixmatch = 'https://api.musixmatch.com/ws/1.1/'
    method = 'artist.search'
    url = base_url_musixmatch + method
    params = {
        'q_artist': artist_name,
        'apikey': api_key,
        'format': 'json'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        artist_list = data.get("message", {}).get("body", {}).get("artist_list", [])
        if artist_list:
            artist = artist_list[0].get("artist", {})
            artist_country = artist.get("artist_country", None)
            if artist_country is not None:
                add_artist_country(artist_name, artist_country, database)
                return artist_country
    return "Error or artist not found"
#fetch song genre from Musixmatch API
#def get_song_genre(api_key, song_name, artist_name=None):
    #base_url_musixmatch = 'https://api.musixmatch.com/ws/1.1/'
    #method = 'track.search'
    #url = base_url_musixmatch + method
    #params = {
       # 'q_track': song_name,
       # 'apikey': api_key,
       # 'format': 'json',
        #'page_size': 150
    #}
    #if artist_name:
        #params['q_artist'] = artist_name
    #response = requests.get(url, params=params)
    ##data = response.json()
        #track_list = data.get("message", {}).get("body", {}).get("track_list", [])
        #for track_info in track_list:
           # track = track_info.get("track", {})
            #if track.get("track_name").lower() == song_name.lower() and \
               #(artist_name is None or track.get("artist_name").lower() == artist_name.lower()):
               # genre_list = track.get("primary_genres", {}).get("music_genre_list", [])
                #if genre_list:
                    #genres = [genre.get("music_genre", {}).get("music_genre_name", "") for genre in genre_list]
                    #return ', '.join(genres)
       # return "Genre not found or exact match not found"
    #else:
        #return f"Error: {response.status_code}"

def main():
    artists = get_artists_from_db(database)
    for artist in artists:
        rating = get_artist_rating_from_musixmatch(artist, api_key)
        if rating is not None:
            add_rating(artist, rating, database)
            print(f"Updated rating: {artist}, Rating: {rating}")
        else:
            print(f"Rating not found: {artist}")

        country = get_artist_country_from_musixmatch(artist, api_key, database)
        if country is not None:
            add_artist_country(artist, country, database)
            print(f"Updated country: {artist}, Country: {country}")
        else:
            print(f"Country not found: {artist}")

    #artists_and_songs = get_artists_and_songs(database)
    #for artist, song in artists_and_songs:
        #genre = get_song_genre(api_key, song, artist)
        #if genre:
            #add_song_genre(artist, song, genre, database)
            #print(f"Updated genre for Artist: {artist}, Song: {song}, Genre: {genre}")
       #else:
            #print(f"Genre not found for Artist: {artist}, Song: {song}")

if __name__ == "__main__":
    main()
