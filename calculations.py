import sqlite3
import datetime as dt
import calendar


def get_top_days(cur, conn):
    '''
    Takes cur and conn, returns a dictionary of weekdays with the number of concerts on each weekday.
    '''
    cur.execute('SELECT date FROM Events')
    days = cur.fetchall()
    weekday_dict = {'Sunday':0,'Monday':0,'Tuesday':0,'Wednesday':0,'Thursday':0,'Friday':0,'Saturday':0}
    for date in days:
    #   print(type(date))
      date = date[0]
      year = int(date[0:4])
      month = int(date[5:7])
      day = int(date[8:])
      # print(f"date: {year}/{month}/{day}")
      datetime_obj = dt.datetime(year, month, day)
      weekday = calendar.day_name[datetime_obj.weekday()]
      weekday_dict[weekday] = weekday_dict.get(weekday, 0) + 1
    conn.commit()
    return weekday_dict


def get_top_countries(cur, conn):
    '''
    Takes cur and conn, returns the top 5 countries based on artists in the database
    '''
    cur.execute('''
                SELECT
                    Countries.name,
                    COUNT(Artists.id)
                FROM Countries
                INNER JOIN Artists ON Artists.country_id = Countries.id
                WHERE Countries.name != ''
                GROUP BY Countries.name
                ORDER BY COUNT(Artists.id) DESC
                LIMIT 5
                ''')
    return [(row[0], row[1]) for row in cur.fetchall()]

    # cur.execute('SELECT country FROM ArtistCountry')
    # countries = cur.fetchall()
    # country_dict = {}
    # for country in countries:
    #     country_dict[country[0]] = country_dict.get(country[0], 0) +1
    # country_list = []
    # for key in country_dict:
    #     if key == '':
    #         continue
    #     else:
    #         country_list.append((key, country_dict[key]))
    # country_list.sort(reverse=True, key=lambda x:x[1])
    # conn.commit()
    # return country_list[0:5]


def get_top_artists(cur, conn):
    '''
    Takes cur and conn, returns the top 15 artists from Artists table
    '''
    cur.execute('SELECT name, plays from Artists')
    artists_plays = cur.fetchall()
    # print(artists_plays[0:15])
    conn.commit()
    return artists_plays[0:15]


def concerts_in_midwest(cur, conn):
    '''
    Takes cur and conn, returns all the events in the Events table that occur in popular Midwest cities
    '''
    list = []
    midwest = ['Minneapolis', 'Pittsburgh', 'Detroit', 'Cincinnati', 'Toronto', 'Philadelphia']
    for city in midwest:
        cur.execute('''
                    SELECT Events.artist_id, Events.city_id, Events.date
                    FROM Cities
                    JOIN Events ON Events.city_id = Cities.id
                    WHERE Cities.name = ?
                    ''', (city,))
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
        cur.execute('SELECT name FROM Cities WHERE id=?',(city_id,))
        city = cur.fetchall()[0][0]
        date = concert[0][2]
        print(f"{artist} in {city} on {date}")
        concerts_list.append({'artist': artist, 'city': city, 'date': date})

    conn.commit()
    return concerts_list



def main():
    conn = sqlite3.connect("music.db")
    cur = conn.cursor()

    get_top_days(cur, conn)
    get_top_countries(cur, conn)
    get_top_artists(cur, conn)
    concerts_in_midwest(cur, conn)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
