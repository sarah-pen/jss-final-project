import sqlite3
import datetime as dt
import calendar

# def avg_min_prices(cur, conn):

#     d = {}
#     for i in range():
#         cur.execute('SELECT min_price FROM Events_final WHERE artist_id=?', (i,))
#         prices = cur.fetchall()[0]

#     return d

# def rating_vs_prices(cur, conn):
#     '''
#     Calculates the ratio of rating to price for each artist and returns a dictionary.
#     '''
#     pass

def get_top_days(cur, conn):
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
    conn.commit()
    # print(country_list[0:5])
    return country_list[0:5]


def get_top_artists(cur, conn):
    cur.execute('SELECT name, plays from Artists')
    artists_plays = cur.fetchall()
    # print(artists_plays[0:15])
    conn.commit()
    return artists_plays[0:15]

def concerts_in_midwest(cur, conn):
    list = []
    cur.execute('SElECT artist_id, city_id, date FROM Events_Final WHERE city_id=15')
    list.append(cur.fetchall())
    cur.execute('SElECT artist_id, city_id, date FROM Events_Final WHERE city_id=23')
    list.append(cur.fetchall())
    cur.execute('SElECT artist_id, city_id, date FROM Events_Final WHERE city_id=62')
    list.append(cur.fetchall())
    cur.execute('SElECT artist_id, city_id, date FROM Events_Final WHERE city_id=13')
    list.append(cur.fetchall())
    cur.execute('SElECT artist_id, city_id, date FROM Events_Final WHERE city_id=7')
    list.append(cur.fetchall())
    cur.execute('SElECT artist_id, city_id, date FROM Events_Final WHERE city_id=11')
    list.append(cur.fetchall())
    concerts_list = []
    for concert in list:
        # concert = concert[0]
        if len(concert) == 0:
            continue
        artist_id = concert[0][0]
        city_id = concert[0][1]
        cur.execute('SELECT name FROM Artists WHERE id=?',(artist_id,))
        artist = cur.fetchall()[0][0]
        cur.execute('SELECT name FROM Cities WHERE city_id=?',(city_id,))
        city = cur.fetchall()[0][0]
        date = concert[0][2]
        print(f"{artist} in {city} on {date}")
        concerts_list.append({'artist': artist, 'city': city, 'date': date})

    conn.commit()
    return concerts_list


conn = sqlite3.connect("music.db")
cur = conn.cursor()

def main():
    # most_common_days_concerts(cur, conn)
    # get_top_countries(cur, conn)
    # get_top_artists(cur, conn)
    concerts_in_midwest(cur, conn)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
