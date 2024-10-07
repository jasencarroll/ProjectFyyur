import psycopg2
from psycopg2.extras import execute_values

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    database="fyyur",
    user="postgres",  # replace with your actual PostgreSQL username
    password="admin"  # replace with your actual PostgreSQL password
)

# Create a cursor object to interact with the database
cur = conn.cursor()

# Fake venue data
venues_data = [
    {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website_link": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    },
    {
        "id": 2,
        "name": "The Dueling Pianos Bar",
        "genres": ["Classical", "R&B", "Hip-Hop"],
        "address": "335 Delancey Street",
        "city": "New York",
        "state": "NY",
        "phone": "914-003-1132",
        "website_link": "https://www.theduelingpianos.com",
        "facebook_link": "https://www.facebook.com/theduelingpianos",
        "seeking_talent": False,
        "seeking_description": None,
        "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80"
    },
    {
        "id": 3,
        "name": "Park Square Live Music & Coffee",
        "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
        "address": "34 Whiskey Moore Ave",
        "city": "San Francisco",
        "state": "CA",
        "phone": "415-000-1234",
        "website_link": "https://www.parksquarelivemusicandcoffee.com",
        "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
        "seeking_talent": False,
        "seeking_description": None,
        "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80"
    }
]

# Define the SQL query for inserting the data
insert_query = """
INSERT INTO public."Venue" (
    id, name, genres, address, city, state, phone, website_link, facebook_link, seeking_talent, seeking_description, image_link
) VALUES %s
ON CONFLICT (id) DO NOTHING;
"""

# Prepare the data to be inserted
venue_values = [
    (
        venue["id"],
        venue["name"],
        venue["genres"],
        venue["address"],
        venue["city"],
        venue["state"],
        venue["phone"],
        venue["website_link"],
        venue["facebook_link"],
        venue["seeking_talent"],
        venue["seeking_description"],
        venue["image_link"]
    )
    for venue in venues_data
]

# Use execute_values to insert all venues in one batch
execute_values(cur, insert_query, venue_values)

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

print("Fake data inserted into the 'venues' table successfully.")
