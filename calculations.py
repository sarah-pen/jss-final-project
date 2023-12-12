import sqlite3
import datetime as dt
import calendar

# Select items from the tables and calculate something from the data (average, counts, etc)
# At least one database join used when selecting the data
# Write a well-formatted, self explanatory file from the calculations (JSON, csv or text file)

def avg_min_prices(cur, conn):

    d = {}
    for i in range(1,7):
        cur.execute('SELECT min_price FROM Events_final WHERE artist_id=?', (i,))
        prices = cur.fetchall()[0]
        # ...
    return d

def rating_vs_prices(cur, conn):
    '''
    Calculates the ratio of rating to price for each artist and returns a dictionary.
    '''
    pass

def most_common_days_concerts(cur, conn):
    '''
    Takes cur and conn, returns a dictionary of weekdays with the number of concerts on each weekday.
    '''
    cur.execute('SELECT date FROM Events_Final')
    days = cur.fetchall()
    weekday_dict = {'Sunday':0, 'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 'Thursday': 0, 'Friday': 0, 'Saturday':0}
    for date in days:
    #   print(type(date))
      date = date[0]
      year = int(date[0:4])
      month = int(date[5:7])
      day = int(date[8:])
      # print(f"date: {year}/{month}/{day}")
      datetime_obj = dt.datetime(year, month, day)
      weekday = calendar.day_name[datetime_obj.weekday()]
      weekday_dict[weekday] += 1
    conn.commit()
    conn.close()
    return weekday_dict

def get_top_genres(cur, conn):
    '''
    takes cur and conn, returns the top 5 genres based on artists in the Database
    '''

def get_top_countries(cur, conn):
    '''
    Takes cur and conn, returns the top 5 countries based on artists in the database
    '''
    cur.execute('SELECT country FROM ArtistCountry')
    countries = cur.fetchall()
    country_dict = {}
    for country in countries:
        country_dict[country[0]] = country_dict.get(country[0], 0) +1
    country_list = []
    for key in country_dict:
        if key == '':
            continue
        else:
            country_list.append((key, country_dict[key]))
    country_list.sort(reverse=True, key=lambda x:x[1])
    # print(country_list[0:5])
    return country_list[0:5]

def get_top_artists(cur, conn):
    cur.execute('SELECT artist from Artists')
    artists = cur.fetchall()



conn = sqlite3.connect("music.db")
cur = conn.cursor()

def main():
    # most_common_days_concerts(cur, conn)
    get_top_countries(cur, conn)

if __name__ == "__main__":
    main()
