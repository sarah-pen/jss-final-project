import lastfm
import musixmatch
import ticketmaster

# Select items from the tables and calculate something from the data (average, counts, etc)
# At least one database join used when selecting the data
# Write a well-formatted, self explanatory file from the calculations (JSON, csv or text file)

def calc_ticketmaster(cur, conn):

    d = {}
    for i in range(1,7):
        cur.execute('SELECT min_price FROM Events_final WHERE artist_id=?', (i,))
        prices = cur.fetchall()[0]
        

    
