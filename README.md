# Fyyur Project

## Overview

Fyyur is a platform designed to help musical artists and venues connect, facilitating the booking and promotion of live shows. The application allows users to create listings for venues and artists, and schedule shows between them. The project builds out a database structure using PostgreSQL, and implements API endpoints to support functionalities like searching for artists and venues, creating new entries, and listing upcoming and past shows.

## Accomplishments

In this project, I developed the data models and implemented the logic that powers the Fyyur platform. Here's what was achieved:

1. **Data Modeling:** I designed normalized data models using SQLAlchemy ORM, ensuring relationships between Artists, Venues, and Shows were correctly represented in the PostgreSQL database. 
2. **Form Handling and Validation:** Integrated forms using Flask-WTF for artist and venue creation, and implemented appropriate data validation for submissions.
3. **Data Migration:** Managed schema migrations with Flask-Migrate to ensure smooth database changes during development.
4. **API Endpoints:** Built API endpoints to allow users to:
   - Create new artists and venues.
   - Schedule shows between artists and venues.
   - Perform partial, case-insensitive searches for artists and venues.
   - View detailed information about individual artists, venues, and shows.
5. **Web Frontend Integration:** Ensured the frontend templates correctly display data from the PostgreSQL database, replacing previous mock data.
6. **Search and Filtering:** Implemented search functionality to allow users to search by partial string matching, filtering results case-insensitively, and properly listing upcoming and past shows.

## Tech Stack

The project is built with the following technologies:

- **Backend:**
  - Python 3 and Flask for server-side logic.
  - SQLAlchemy ORM for database modeling.
  - PostgreSQL as the database engine.
  - Flask-Migrate for database schema migrations.
  
- **Frontend:**
  - HTML, CSS, and JavaScript for the web interface.
  - Bootstrap 3 for responsive design.
  
## Project Structure

```bash
ProjectFyyur/
│── README.md                # Project documentation
│── fyyur.py                 # Main app file for running the Flask server
│── config.py                # Configuration settings for the app (e.g., database URI)
│── requirements.txt         # List of Python dependencies to install
│── error.log                # Log file for application errors
│── fabfile.py               # Fabric commands for automation or deployment
│── .flaskenv                # Flask environment variables (e.g., FLASK_APP, FLASK_ENV)
│── migrations/              # Directory containing database migration files for Flask-Migrate
│── load_files/              # Contains files for seeding initial data into the database
│── static/                  # Directory for static assets (CSS, JS, images)
│── templates/               # HTML templates for rendering views
│── node_modules/            # Node.js dependencies for frontend development
│── app/                     # Main application module
│   ├── __init__.py          # Initializes the app and sets up the Flask application factory
│   ├── models.py            # SQLAlchemy models for database tables
│   ├── forms.py             # Flask-WTF forms for handling user input
│   ├── routes.py            # Flask routes defining the application's URL endpoints
│   ├── filters.py           # Custom Jinja filters for use in templates
├── package.json             # Frontend dependencies and scripts for Node.js
├── package-lock.json        # Locks Node.js package versions for consistent builds
```

## Setting Up the Development Environment

To run this project locally, follow the steps below:

1. **Clone the Repository**
   
   ```bash
   git clone https://github.com/your_username/fyyur.git
   cd fyyur
   ```

2. **Set up a Virtual Environment**
   
   Create and activate a Python virtual environment:
   
   ```bash
   python -m virtualenv env
   source env/bin/activate  # On Windows: source env/Scripts/activate
   ```

3. **Install Dependencies**
   
   Install the required Python packages:
   
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Database**

   In `config.py`, update the `SQLALCHEMY_DATABASE_URI` to point to your PostgreSQL instance. For example:
   
   ```python
   SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:5432/fyyurdb'
   ```

5. **Run Database Migrations**

   Initialize the database schema:
   
   ```bash
   flask db upgrade
   ```

6. **Run the Application**

   Set environment variables and start the development server:
   
   ```bash
   export FLASK_APP=app.py
   export FLASK_ENV=development
   flask run
   ```

   Alternatively, for Windows:
   
   ```bash
   set FLASK_APP=app.py
   set FLASK_ENV=development
   flask run
   ```

7. **Access the App**

   Open your browser and navigate to [http://127.0.0.1:5000/](http://127.0.0.1:5000/) to access the Fyyur app.

## Troubleshooting

- If you encounter any dependency issues, ensure you're using Python 3.9 or lower.
- If database migrations fail, ensure PostgreSQL is running and properly configured.

## Future Enhancements

Possible future improvements include:
- Implementing artist availability features for more precise show scheduling.
- Adding sorting and filtering options for recently added venues and artists on the homepage.
- Extending search functionality to include location-based filtering by city and state.

---

This project brings the Fyyur platform to life by enabling real data to flow through the application and integrating database functionality for managing musical venues, artists, and shows.