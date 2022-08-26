import sqlite3

connection = sqlite3.connect('points_submissions.db')

cursor = connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS Spins
              (User_id INTEGER, Name TEXT, Date INT)''')

connection.commit()
connection.close()