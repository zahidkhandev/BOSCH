import sqlite3
from pathlib import Path
from pprint import pp
import pprint

db_path = Path("/home/zadmin/BOSCH/dbms/sqlite/db/example.sqlite")

db = sqlite3.connect(db_path, isolation_level=None)

# try:
#     db.execute('CREATE TABLE IF NOT EXISTS cats (name TEXT NOT NULL, birthdate TEXT, fur TEXT, weight_kg REAL) STRICT')
#     print("Table created")
# except sqlite3.OperationalError:
#     print("Table already exists")


print(db.execute('SELECT * FROM sqlite_schema WHERE type="table"').fetchall())
# all_cats = db.execute("SELECT * FROM cats")
print(db.execute('PRAGMA TABLE_INFO(cats)').fetchall())
# print(all_cats)

db.execute('INSERT INTO cats VALUES ("Zophie", "2021-01-24", "black", 5.6)')
print(db.execute('SELECT rowid, * FROM cats ORDER BY fur').fetchall())
db.execute('UPDATE cats SET fur = "gray tabby" WHERE rowid = 1')
db.execute('DELETE FROM cats WHERE rowid = 1')
print(db.execute('SELECT rowid, * FROM cats ORDER BY fur').fetchall())

cat_name = 'Zophie'
cat_bday = '2021-01-24'
fur_color = 'black'
cat_weight = 5.6

# If the values of these variables came from user input such as a web app form, a hacker could potentially specify strings 
# that changed the meaning of the query. Instead, I should use a ? in the query string, then pass the variables in a list
# argument following the query string:
db.execute('INSERT INTO cats VALUES (?, ?, ?, ?)', [cat_name, cat_bday, fur_color, cat_weight])

print(db.execute('SELECT * FROM cats').fetchall())

for row in db.execute('SELECT * FROM cats'):
    print('Row data:', row)
    print(row[0], 'is one of my favorite cats.')

print(db.execute('SELECT * FROM cats WHERE fur = "black"').fetchall())

matching_cats = db.execute('SELECT * FROM cats WHERE fur = "black" OR birthdate >= "2024-01-01"').fetchall()

# pretty print
pprint.pprint(matching_cats)

pprint.pprint(db.execute('SELECT * FROM cats ORDER BY fur').fetchall())

# Limit results to 3
pprint.pprint(db.execute('SELECT * FROM cats LIMIT 3').fetchall())
pprint.pprint(db.execute('SELECT * FROM cats WHERE fur="black" ORDER BY birthdate LIMIT 4').fetchall())

# Create an index for efficient quering
db.execute('CREATE INDEX IF NOT EXISTS cats_name ON cats (name)')
db.execute('CREATE INDEX IF NOT EXISTS cats_birthdate ON cats (birthdate)')

# Print all indexes:
pp(db.execute('SELECT name FROM sqlite_schema WHERE type = "index" AND tbl_name = "cats"').fetchall())
# Drop an index
db.execute('DROP INDEX IF EXISTS cats_birthdate')

pp(db.execute('SELECT name FROM sqlite_schema WHERE type = "index" AND tbl_name = "cats"').fetchall())

db.execute('UPDATE cats SET fur = "gray tabby" WHERE rowid = 5')

pp(db.execute('SELECT * FROM cats WHERE rowid = 5').fetchall())