# Game Service

- `gamedb.db` แยกกับ local db ของเกมนะ จำลองว่าเป็น db ฝั่ง game server ละกัน  

# Score service
- `score_service.py` เป็นตัวคอย record score ลง gamedb คอย subscribe ที /score  
- เวลารัน `score_service` ถ้าไม่มี ./gamedb.db จะสร้างให้ตอนแรก

# Score submission

ดูตัวอย่างที่ game client จะต้องส่ง end-game result ไปให้ score service ได้ที่ `test_socre_producer.py` และใช้ไฟล์นี้ในการยัด score แบบ manual ได้ (ค่าอื่น ๆ random เอา)

### Score message format
```python
""" 
1624164210.0624566,user-1,700,111.8,128.3,201,324,398,197
"""

ts = time.time()
user_id = 'user-1'
score = 700
pos_x = 111.8 (mean of x coordinates)
pos_y = 128.3 (mean of y coordinates)
kill = 201
coin = 324
shot = 398
miss = shot - kill

msg = f"{ts},{user_id},{score},{pos_x},{pos_y},{kill},{coin},{shot},{miss}" # shot with out kill

# Netpie send
client.connect(False)
client.publish('/score', msg)
time.sleep(wait)
```

# High score
- `highscore_publisher.py` จะคอยอ่าน gamedb ทุก 5 วิ แล้ว publish ออก /highscore  

### High score message format

ดูตัวอย่างการรับ high score ได้ที่ `test_highscore_sub.py` 

```python
"""
user-1,700,user-6,650,user-7,550
"""
def parse_message(msg):
    tokens = msg[2:-1].split(',')

    highscores = list(zip(range(1, len(tokens)//2+1), tokens[0::2], tokens[1::2]))
    return highscores

def print_highscores(highscores):
    for s in highscores:
        print(f"{s[0]}: {s[1]} {s[2]}")
        
 def callback_message(topic, message) :
    print(topic, message)
    highscores = parse_message(message)
    print_highscores(highscores)
    
client.subscribe("/highscore") 
client.connect(True)

""" Example output
1: user-1 700
2: user-6 650
3: user-7 550
"""
```

ปัญหาตอนนี้อยู่ที่ client.connect(True) น่าคอยรับค้าง ถ้าเอาไปใส่ไว้ในตัวเกมน่าจะ block การทำงานของเกม


