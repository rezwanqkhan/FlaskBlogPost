import sqlite3

# Connect to the SQLite database
connection = sqlite3.connect("database.db")


# Open the SQL file containing schema definition
with open('schema.sql') as f:
    # Execute the SQL script to create tables and schema
    connection.executescript(f.read())

# Create a cursor object to execute SQL queries
cur = connection.cursor()
# Set the username of the user you want to promote to admin
username = "rezwan"

# Execute an SQL UPDATE statement to set the is_admin column to 1 for the specified user
cur.execute("UPDATE users SET is_admin = 1 WHERE username = ?", (username,))

# Commit the changes
connection.commit()

# Close the connection
connection.close()
