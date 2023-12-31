import requests
import sqlite3
import json
import matplotlib.pyplot as plt

api_key = "4ced0fe04de2090cb8f068ca309e8d96"
base_url = "https://api.musixmatch.com/ws/1.1/"
database = "music.db"

#checks if existing data for artist exists
def artist_populated(artist_name, database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM Artists WHERE name = ? AND country_id IS NOT NULL AND rating IS NOT NULL', (artist_name,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

#inserts or updates the artist's rating.
def add_rating(artist_name, rating, database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    # cursor.execute('INSERT OR IGNORE INTO Ratings (artist, rating) VALUES (?, ?)', (artist_name, rating))
    cursor.execute('UPDATE Artists SET rating = ? WHERE name = ?', (rating,artist_name))
    conn.commit()
    conn.close()

#inserts or updates the artist's country
def add_artist_country(artist_name, country, database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO Countries (name) VALUES (?)', (country,))
    cursor.execute('UPDATE Artists SET country_id = (SELECT id FROM Countries WHERE name = ?) WHERE name = ?', (country,artist_name))
    conn.commit()
    conn.close()

#retrieves a list of artist names from the SQLite database.
def get_artists_from_db(database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Artists")
    artists = cursor.fetchall()
    conn.close()
    artist_names = [artist[0] for artist in artists]
    return artist_names

#fetch the artist's rating from the Musixmatch API and return rating
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

#fetch artist country from Musixmatch API and return country information
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

def main():
    artists = get_artists_from_db(database)
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Countries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE
                   )
                   ''')

    conn.commit()
    conn.close()

    for artist in artists:
        if not artist_populated(artist, database):
            rating = get_artist_rating_from_musixmatch(artist, api_key)
            country = get_artist_country_from_musixmatch(artist, api_key, database)
            if rating is not None and country is not None:
                add_rating(artist, rating, database)
                add_artist_country(artist, country, database)
                print(f"Updated rating: {artist}, Rating: {rating}")
                print(f"Updated country: {artist}, Country: {country}")
            else:
                print(f"Rating or country not found fir: {artist}")
        else:
            print(f"Rating for {artist} already exists.")



if __name__ == "__main__":
    main()
