import requests
import sqlite3

api_key = "28057900aa8badddae0f85dbdfb8848b"
username = "Sarah297"
base_url = 'http://ws.audioscrobbler.com/2.0/'

def get_username():
    user = input("What is your last.fm username?")
    username = user

def get_top_artist(api_key, username, period='overall', limit=1):

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

    for i in range(limit):
        artist = data['topartists']['artist'][i]
        name = artist['name']
        plays = artist['playcount']
        print(f"{i+1}) {name} - {plays} plays")

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
    for track in data: # track is a dictionary
        artist = track['artist']['#text']
        track_name = track['name']
        print(f"{artist}: {track_name}")
    return data

    pass


def main():
    data = "Meow"
    # get_top_artist(api_key, username, period="overall", limit=2)
    data = get_recent_plays(api_key, username, limit=20)


if __name__ == "__main__":
    main()
