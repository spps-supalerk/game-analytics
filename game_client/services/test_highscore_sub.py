import microgear.client as client
import logging
import time
import sqlite3
from datetime import datetime

DATABASE = './gamedb.db'

# NetPie client
# key: sub-highscore
appid = 'MookataGame'
gearkey = 'Q1GXcLhGXDHKqLH'
gearsecret = 'dojFgPxaY0yY901bwK4YmWx6V'

client.create(gearkey,gearsecret,appid,{'debugmode': True}) # สร้างข้อมูลสำหรับใช้เชื่อมต่อ
client.setalias("test-highscore-sub")

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
    highscores = parse_message(message)
    print_highscores(highscores)

def callback_error(msg) :
    print("error", msg)

client.on_connect = callback_connect 
client.on_message= callback_message 
client.on_error = callback_error 
client.subscribe("/highscore") 
client.connect(True)