import microgear.client as client
import logging
import time
import sqlite3
from datetime import datetime

DATABASE = './gamedb.db'

sql_insert = """
insert into gamestat(timestamp, user, score, pos_x, pos_y, kill, coin, shot, miss, client_timestamp) 
values(strftime('%Y-%m-%d %H:%M:%S','now'),?,?,?,?,?,?,?,?,?)
"""

# NetPie client
# key: sub-score
appid = 'MookataGame'
gearkey = 'Ia5lxolZWf7O9fE'
gearsecret = 'uZcDqIZ0yopoGVtpIhpA8MwMZ'

client.create(gearkey,gearsecret,appid,{'debugmode': True}) # สร้างข้อมูลสำหรับใช้เชื่อมต่อ
client.setalias("score-service")

def parse_message(msg):
    tokens = msg[2:-1].split(',')
    client_ts = datetime.fromtimestamp(float(tokens[0])).strftime('%Y-%m-%d %H:%M:%S')
    username = tokens[1]
    score = int(tokens[2])
    pos_x = float(tokens[3])
    pos_y = float(tokens[4])
    kill = int(tokens[5])
    coin = int(tokens[6])
    shot = int(tokens[7])
    miss = int(tokens[8])
    return (username, score, pos_x, pos_y, kill, coin, shot, miss, client_ts)

def callback_connect() :
    print ("Now I am connected with netpie")
    
def callback_message(topic, message) :
    print(topic, message)
    parsed_msg = parse_message(message)
    print('parsed msg:', parsed_msg)

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(sql_insert, parsed_msg)
        conn.commit()
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if conn:
            conn.close()


def callback_error(msg) :
    print("error", msg)

# if the database is not there, create it

def init_db():
    sql_create_table = """
    CREATE TABLE IF NOT EXISTS gamestat (
        id integer PRIMARY KEY AUTOINCREMENT,
        timestamp text,
        user text,
        score integer,
        pos_x real,
        pos_y real,
        kill integer,
        coin integer,
        shot integer,
        miss integer,
        client_timestamp text
    );
    """

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(sql_create_table)
    conn.commit()
    conn.close()

init_db()

client.on_connect = callback_connect 
client.on_message= callback_message 
client.on_error = callback_error 
client.subscribe("/score") 
client.connect(True)