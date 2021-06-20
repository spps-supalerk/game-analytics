# Game Service

- `gamedb.db` แยกกับ local db ของเกมนะ จำลองว่าเป็น db ฝั่ง game server ละกัน  

- `score_service.py` เป็นตัวคอย record score ลง gamedb คอย subscribe ที /score  
- เวลารัน `score_service` ถ้าไม่มี ./gamedb.db จะสร้างให้ตอนแรก

- `highscore_publisher.py` จะคอยอ่าน gamedb ทุก 5 วิ แล้ว publish ออก /highscore  
