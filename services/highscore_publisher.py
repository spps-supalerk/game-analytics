import microgear.client as client
import logging
import time
import sqlite3
from datetime import datetime

DATABASE = './gamedb.db'

# NetPie client
# Key: pub-highscore
appid = 'MookataGame'
gearkey = '5aTga8Ic047dpQI'
gearsecret = 'icVIYaxXJp9ltF8XwMM5MAS3k'

client.create(gearkey,gearsecret,appid,{'debugmode': True}) 
client.setalias("highscore-publisher")

sql_query = """
select user, max_score
from (
    select user, max(score) as max_score
    from gamestat
    group by user
) order by max_score desc
limit 5
"""

def callback_connect() :
    print ("Now I am connected with netpie")
    
def callback_message(topic, message) :
    print(topic, message)


def callback_error(msg) :
    print("error", msg)

def format_message(rs):
    return ','.join(map(lambda x: ','.join(map(str, x)),rs))

client.on_connect = callback_connect 
client.on_message= callback_message 
client.on_error = callback_error 
# client.subscribe("/highscore") 
client.connect(False)

wait = 3
rs = []
while True:
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rs = cursor.fetchall()
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if conn:
            conn.close()

    msg = format_message(rs)
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(ts,':',msg)

    client.publish('/highscore', msg)
    time.sleep(wait)