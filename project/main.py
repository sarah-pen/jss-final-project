import lastfm
import musixmatch
import ticketmaster
import calculations
import sqlite3
import matplotlib.pyplot as plt
import numpy as np

def build_database():
  lastfm.main()
  musixmatch.main()
  ticketmaster.main()


def do_calculations():
  conn = sqlite3.connect('music.db')
  cur = conn.cursor()

  # TODO: Call function to get dictionary of each day of the week
  days = calculations.get_top_days(cur, conn)
  fig, ax = plt.subplots()
  weekdays = []
  counts = []
  for day in days:
     weekdays.append(day[0:3])
     counts.append(days[day])
  sumcount = sum(counts)
  for i in range(len(counts)):
     counts[i] /= sumcount
     counts[i] *= 100
  colors = ['red', 'blue', 'blue', 'blue', 'blue', 'blue', 'red']
  ax.bar(weekdays, counts, color=colors)

  ax.set_ylabel('Percentage of Concerts')
  ax.set_title('Concerts per Weekday')
  plt.savefig('output/Weekdays.png')


  # TODO: Top countries of artists
  countries = calculations.get_top_countries(cur, conn)
  artists = []
  amounts = []
  for country in countries:
    artists.append(country[0])
    amounts.append(int(country[1]))
  fig, ax = plt.subplots()
  ax.pie(amounts, labels=artists, autopct='%1.1f%%')
  ax.set_title('Top 5 Countries of Artists')
  plt.savefig('output/Countries.png')


  # TODO: Top artists bar graph
  artists = calculations.get_top_artists(cur, conn)
  fig, ax = plt.subplots()
  names = []
  playcounts = []
  for artist in artists:
     names.append(artist[0])
     playcounts.append(int(artist[1]))
  names.reverse()
  playcounts.reverse()
  y_pos = np.arange(len(names))
  ax.barh(y_pos, playcounts)
  ax.set_yticks(y_pos, labels=names)
  ax.set_xlabel('Times Listened')
  ax.set_title('Number of Times Listened to Artist')
  plt.savefig('output/TopArtists.png', bbox_inches='tight')

  # Concerts
  concerts = calculations.concerts_in_midwest(cur, conn)

  # Write to file
  outfile = open('output/report.txt', 'w')
  outfile.write("SI 206: Our Findings\n")
  outfile.write('\n')

  outfile.write("Our first metric that we calculated was the percentage of concerts that occured on each day of the week, based on a sampling of artists from TicketMaster.\n")
  for day in days:
    days[day] /= sumcount
    days[day] *= 100
    days[day] = int(days[day])
    outfile.write(f"{day}: {days[day]}% of concerts\n")

  outfile.write('\n')
  outfile.write("Our second metric that we calculated was the top artists listened to by the user, which in this case is Sarah H.\n")
  for artist in artists:
    outfile.write(f"{artist[0]}: {artist[1]} total plays\n")

  outfile.write('\n')
  outfile.write("Our third metric that we calculated was the top 5 countries that all of the user's artists are from.\n")
  for country in countries:
    outfile.write(f"{country[0]}: {country[1]} artists\n")

  outfile.write('\n')
  outfile.write('Here is a list of concerts in the Midwest, based on your top artists:\n')
  for concert in concerts:
    outfile.write(f"{concert['artist']} in {concert['city']} on {concert['date']}\n")

  outfile.close()

  conn.commit()
  conn.close()


def main():
  # lastfm.delete_artists_table()
  build_database()
  do_calculations()

if __name__ == "__main__":
    main()
