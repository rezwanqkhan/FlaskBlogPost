import sqlite3
from faker import Faker

# Connect to the SQLite database
connection = sqlite3.connect("database.db")

# Open the SQL file containing schema definition
with open('schema.sql') as f:
    # Execute the SQL script to create tables and schema
    connection.executescript(f.read())

# Create a cursor object to execute SQL queries
cur = connection.cursor()

# Use Faker to generate example users with unique email addresses
fake = Faker()
for _ in range(5):  # Change 5 to the number of users you want to generate
    username = fake.user_name()
    email = fake.email()
    cur.execute("INSERT INTO users (username, email) VALUES (?, ?)", (username, email))
    user_id = cur.lastrowid  # Get the ID of the last inserted user

    # Insert data into the 'posts' table, associating each post with a user
    cur.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)", ('First Post', 'Content for the first post', user_id))
    cur.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)", ('Second Post', 'Content for the second post', user_id))

# Commit the changes
connection.commit()

# Close the connection
connection.close()
