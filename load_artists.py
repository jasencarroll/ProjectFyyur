import psycopg2
from psycopg2.extras import execute_values

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    database="fyyur",
    user="your_username",  # replace with your actual PostgreSQL username
    password="your_password"  # replace with your actual PostgreSQL password
)

# Create a cursor object to interact with the database
cur = conn.cursor()

# Fake artist data
artists_data = [
    {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    },
    {
        "id": 5,
        "name": "Matt Quevedo",
        "genres": ["Jazz"],
        "city": "New York",
        "state": "NY",
        "phone": "300-400-5000",
        "website": None,  # No website provided for this artist
        "facebook_link": "https://www.facebook.com/mattquevedo923251523",
        "seeking_venue": False,
        "seeking_description": None,
        "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80"
    },
    {
        "id": 6,
        "name": "The Wild Sax Band",
        "genres": ["Jazz", "Classical"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "432-325-5432",
        "website": None,  # No website provided for this artist
        "facebook_link": None,  # No Facebook link provided for this artist
        "seeking_venue": False,
        "seeking_description": None,
        "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80"
    }
]

# Define the SQL query for inserting the data
insert_query = """
INSERT INTO artists (
    id, name, genres, city, state, phone, website, facebook_link, seeking_venue, seeking_description, image_link
) VALUES %s
ON CONFLICT (id) DO NOTHING;
"""

# Prepare the data to be inserted
artist_values = [
    (
        artist["id"],
        artist["name"],
        artist["genres"],
        artist["city"],
        artist["state"],
        artist["phone"],
        artist["website"],
        artist["facebook_link"],
        artist["seeking_venue"],
        artist["seeking_description"],
        artist["image_link"]
    )
    for artist in artists_data
]

# Use execute_values to insert all artists in one batch
execute_values(cur, insert_query, artist_values)

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

print("Fake artist data inserted into the 'artists' table successfully.")
