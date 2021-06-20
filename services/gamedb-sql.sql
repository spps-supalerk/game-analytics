select * from gamestat;

delete from gamestat;


-- get top 3 high score
select user, score
from gamestat order by score desc, timestamp
limit 3

DROP TABLE gamestat;

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
