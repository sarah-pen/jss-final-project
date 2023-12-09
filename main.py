import lastfm
import musixmatch
import ticketmaster

database = 'music.db'


def build_database():
  artist_list = lastfm.get_top_artists(lastfm.api_key, lastfm.username, period="overall", limit=100)
  lastfm.insert_data_into_table(artist_list[0:25])
  lastfm.insert_data_into_table(artist_list[26:50])
  lastfm.insert_data_into_table(artist_list[51:75])
  lastfm.insert_data_into_table(artist_list[76:100])

  # TODO:
  # Get Min/Max ticket prices for each artist (or null if artist isn't active)
  # Genre(s) for each artist - make a pie chart
  # Make another database that stores top songs and links to artist database
  # Possibly most common locations for concerts

def main():
  build_database()
