import microgear.client as client
import time 
import random
import numpy as np

# key: pub-score
appid = 'MookataGame'
gearkey = 'dXvAQQ9iynSBwPu'
gearsecret = 'UwSEGPJuZN3yW3wnZwhWYtAd6'

client.create(gearkey,gearsecret,appid,{'debugmode': True}) # สร้างข้อมูลสำหรับใช้เชื่อมต่อ

client.setalias("test-client")

def callback_connect() :
    print ("Now I am connected with netpie")

def callback_message(topic, message) :
    print (topic, ": ", message)

def callback_error(msg) :
    print(msg)

def generate_random_message(score=None):
    x_coord = random.choices(range(256),k=10)
    y_coord = random.choices(range(256),k=10)
    ts = time.time()       # 0
    user_id = f"user-{random.randint(1,9)}"    # 1

    score = score if score else random.gauss(8000,3000)
    score = int(score   ) if score > 0 else 0    # 2
    pos_x = np.mean(x_coord) # 3
    pos_y = np.mean(y_coord) # 4
    kill = random.randint(0,500) # 5
    coin = random.randint(0,500)  # 6
    shot = random.randint(0,1000) # 7
    msg = f"{ts},{user_id},{score},{pos_x},{pos_y},{kill},{coin},{shot}"
    return msg

client.on_connect = callback_connect # แสดงข้อความเมื่อเชื่อมต่อกับ netpie สำเร็จ
client.on_message= callback_message # ให้ทำการแสดงข้อความที่ส่งมาให้
client.on_error = callback_error # หากมีข้อผิดพลาดให้แสดง
# client.subscribe("/score") # ชื่อช่องทางส่งข้อมูล ต้องมี / นำหน้า และต้องใช้ช่องทางเดียวกันจึงจะรับส่งข้อมูลระหว่างกันได้

client.connect(False) # เชื่อมต่อ ถ้าใช้ False ไม่ค้างการเชื่อมต่อ
scores = list(map(int, input('test: ').strip().split(',')))
wait = 1
for score in scores:
    msg = generate_random_message(score=score)
    print(msg)
    client.publish('/score', msg)
    time.sleep(wait)

print("Completed...")