import microgear.client as client
import logging
import time
import sqlite3
from datetime import datetime
from multiprocessing import Process
import pickle

DATABASE = './gamedb.db'
TEMP_FILE = './temp.pkl'

highscores = []


# NetPie client
# key: sub-highscore
appid = 'MookataGame'
gearkey = 'Q1GXcLhGXDHKqLH'
gearsecret = 'dojFgPxaY0yY901bwK4YmWx6V'

client.create(gearkey,gearsecret,appid,{'debugmode': True}) # สร้างข้อมูลสำหรับใช้เชื่อมต่อ
client.setalias("test-game-client")


def parse_message(msg):
    tokens = msg[2:-1].split(',')

    highscores = list(zip(range(1, len(tokens)//2+1), tokens[0::2], tokens[1::2]))
    return highscores

def print_highscores(highscores):
    for s in highscores:
        print(f"{s[0]}: {s[1]} {s[2]}")

def callback_connect() :
    print ("Now I am connected with netpie")
    
def callback_message(topic, message) :
    print(topic, message)
    hs_data = parse_message(message)
    with open('temp.pkl', 'wb') as f:
        pickle.dump(hs_data, f)

def callback_error(msg) :
    print("error", msg)

client.on_connect = callback_connect 
client.on_message= callback_message 
client.on_error = callback_error 
client.subscribe("/highscore") 

def highscore_subscriber():
    client.connect(True)

if __name__ == '__main__':

    p = Process(target=highscore_subscriber)
    p.start()
    tick = time.time()

    while True:
        tock = time.time()

        # print high scores every 5 seconds
        if tock - tick > 5:
            with open(TEMP_FILE, 'rb') as f:
                highscores = pickle.load(f)
            tick = tock # reset timer

        print(time.time())
        print_highscores(highscores)

        time.sleep(.5)

    p.join()


