import sqlite3
# script in db
# Connect to the SQLite database
connection = sqlite3.connect("database.db")

# Open the SQL file containing schema definition
with open('scheme.sql') as f:
    # Execute the SQL script to create tables and schema
    connection.executescript(f.read())

# Create a cursor object to execute SQL queries
cur = connection.cursor()

# Insert data into the 'posts' table
cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)", ('First Post', 'Content for the first post'))
cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)", ('Second Post', 'Content for the second post'))

# Commit the changes
connection.commit()

# Close the connection
connection.close()
