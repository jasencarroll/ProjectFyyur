import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    database="fyyur",
    user="postgres",  # replace with your actual PostgreSQL username
    password="admin"  # replace with your actual PostgreSQL password
)

# Create a cursor object to interact with the database
cur = conn.cursor()

# Example show data
shows_data = [
    {
        "venue_id": 1,
        "artist_id": 4,
        "start_time": "2019-05-21T21:30:00.000Z"
    },
    {
        "venue_id": 3,
        "artist_id": 5,
        "start_time": "2019-06-15T23:00:00.000Z"
    },
    {
        "venue_id": 3,
        "artist_id": 6,
        "start_time": "2035-04-01T20:00:00.000Z"
    },
    {
        "venue_id": 3,
        "artist_id": 6,
        "start_time": "2035-04-08T20:00:00.000Z"
    },
    {
        "venue_id": 3,
        "artist_id": 6,
        "start_time": "2035-04-15T20:00:00.000Z"
    }
]

# Define the SQL query for inserting the show data
insert_query = """
INSERT INTO public."Show" (venue_id, artist_id, start_time)
VALUES %s;
"""

# Prepare the data to be inserted (convert start_time to datetime object)
show_values = [
    (
        show["venue_id"],
        show["artist_id"],
        datetime.strptime(show["start_time"], "%Y-%m-%dT%H:%M:%S.%fZ")
    )
    for show in shows_data
]

# Use execute_values to insert all shows in one batch
execute_values(cur, insert_query, show_values)

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

print("Fake show data inserted into the 'shows' table successfully.")
