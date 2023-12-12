import lastfm
import musixmatch
import ticketmaster
import calculations

database = 'music.db'

def build_database():
  artist_list = lastfm.get_top_artists(lastfm.api_key, lastfm.username, period="overall", limit=100)

  lastfm.insert_data_into_table(artist_list[0:25])
  lastfm.insert_data_into_table(artist_list[26:50])
  lastfm.insert_data_into_table(artist_list[51:75])
  lastfm.insert_data_into_table(artist_list[76:100])

  # print(f"inserted {len(artist_list)} artists")

  # TODO:

  # Get Min/Max ticket prices for each artist (or null if artist isn't active)
  # Make another database that stores top songs and links to artist database

  # VISUALIZATIONS:
  # Country of origin for each artist - make a pie chart
  # Possibly most common locations for concerts
  # Top artists by playcount (bar graph)
  # Rating vs. Ticket Price

def calculations():
  pass
   # TODO: Call calculations.most_common_days_concerts
   # store results to file and make visualization


   # TODO: Top countries of artists
   # store results to file and make visualization

   # TODO: Top artists bar graph
   # store results to file and make visualization

def main():
  build_database()

if __name__ == "__main__":
    main()
