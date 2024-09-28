import sqlite3

connection = sqlite3.connect("sweep.db")
connection.row_factory = sqlite3.Row
cursor = connection.cursor()
connection.commit()
cursor.execute("CREATE TABLE subnet(ID INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT, mac TEXT, pingable INT);")
connection.commit()


