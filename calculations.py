import sqlite3

# Select items from the tables and calculate something from the data (average, counts, etc)
# At least one database join used when selecting the data
# Write a well-formatted, self explanatory file from the calculations (JSON, csv or text file)

def min_prices(conn, cur):

    '''Calculates the average minimum ticket price for each artist in the table'''

    d = {}
    for i in range(1,7):
        cur.execute('SELECT min_price FROM Events_Final WHERE artist_id=?', (i,))
        min_prices = cur.fetchall()
        total = 0
        for price in min_prices:
            if price[0] == None:
                continue
            total += price[0]
        avg_min = total / len(price)
        cur.execute('SELECT name FROM Touring_Artists WHERE artist_id=?', (i,))
        artist = cur.fetchone()[0]
        d[artist] = avg_min

    conn.commit()
    return d







database = "music.db"
conn = sqlite3.connect(database)
cur = conn.cursor()
print(min_prices(conn, cur))
        
        

    
