import requests
import json
import sqlite3

def index():
    re = requests.get('https://api.nobitex.ir/v2/orderbook/USDTIRT')
    req = requests.get('https://api.nobitex.ir/v2/orderbook/USDTIRT').content
    data = json.loads(req)
    usdtirt_price = data['lastTradePrice'][0:-1]
    return usdtirt_price

data = index()

conn = sqlite3.connect('crondata.db')
c = conn.cursor()

# Create the data_table table if it does not exist
c.execute('CREATE TABLE IF NOT EXISTS data_table (number_column TEXT)')

c.execute('SELECT COUNT(*) FROM data_table')
count = c.fetchone()[0]

if count == 0:
    c.execute('INSERT INTO data_table (number_column) VALUES (?)', (data,))
else:
    c.execute('DELETE FROM data_table WHERE ROWID = (SELECT MIN(ROWID) FROM data_table)')
    c.execute('INSERT INTO data_table (number_column) VALUES (?)', (data,))

conn.commit()
conn.close()