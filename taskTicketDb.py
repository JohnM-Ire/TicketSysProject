
import sqlite3

conn = sqlite3.connect('mainDatabase.db')
conn.execute('CREATE TABLE USER (user_id INTEGER NOT NULL AUTOINCREMENT,'
             ' username VARCHAR(30), name VARCHAR(50), email VARCHAR(50), '
             'jobTitle VARCHAR(60), taskComplete INTEGER,password VARCHAR(12), dateAdded DATETIME)')

