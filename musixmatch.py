import requests
import sqlite3
import json
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

api_key = "4ced0fe04de2090cb8f068ca309e8d96"
base_url = "https://api.musixmatch.com/ws/1.1/"

#creates a table if it doesn't exist and inserts or updates the artist's rating.
def cache_rating(artist_name, rating, database='ratings.db'):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS Ratings (artist TEXT PRIMARY KEY, rating INTEGER)')
    cursor.execute('INSERT OR REPLACE INTO Ratings (artist, rating) VALUES (?, ?)', (artist_name, rating))
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
                cache_rating(artist_name, artist_rating)
            return artist_rating
    return "Error or artist not found"

def main():
    test_artists = ["Queen", "The Beatles", "Adele", "One Direction"]
    for artist in test_artists:
        rating = get_artist_rating_from_musixmatch(artist, api_key)
        print(f"Artist: {artist}, Rating: {rating}")

if __name__ == "__main__":
    main()
