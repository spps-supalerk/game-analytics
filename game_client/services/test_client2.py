import microgear.client as client
import logging
import time
import sqlite3
from datetime import datetime
from multiprocessing import Process
import pickle
from multiprocessing import Process, Lock
from multiprocessing.sharedctypes import Value, Array
import ctypes

# DATABASE = './gamedb.db'
# TEMP_FILE = './temp.pkl'

# initlize msg buffer (array of byte - size=100)
msg_buffer = Array('c', (" "*100).encode('utf-8'), lock=False)




def parse_message(msg):
    tokens = msg.decode('utf-8')[2:-1].split(',')

    highscores = list(zip(range(1, len(tokens)//2+1), tokens[0::2], tokens[1::2]))
    return highscores

def print_highscores(highscores):
    if highscores: 
        for s in highscores:
            print(f"{s[0]}: {s[1]} {s[2]}")
    else:
        print('no scores')

# Process 2
def highscore_subscriber(msg_buffer):

    def callback_connect():
        print ("Now I am connected with netpie")

    def callback_error(msg) :
        print("error", msg)

    def callback_message(topic, message) :
        print(topic, message)
        msg_buffer.value = message.encode('utf-8')
    
    # NetPie client
    # key: sub-highscore
    appid = 'MookataGame'
    gearkey = 'Q1GXcLhGXDHKqLH'
    gearsecret = 'dojFgPxaY0yY901bwK4YmWx6V'

    client.create(gearkey,gearsecret,appid,{'debugmode': True})
    client.setalias("test-game-client")
    client.on_connect = callback_connect 
    client.on_message = callback_message
    client.on_error = callback_error 
    client.subscribe("/highscore") 
    client.connect(True)

if __name__ == '__main__':

    p = Process(target=highscore_subscriber, args=(msg_buffer,))
    p.start()
    

    # Game loop
    while True:

        print('game loop:', time.time())
        msg = msg_buffer.value
        
        print_highscores(parse_message(msg))

        time.sleep(1)

    p.join()


