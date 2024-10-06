from app import app, db
import logging
from logging import Formatter, FileHandler
from sqlalchemy import func
from flask import render_template, request, flash, redirect, url_for, jsonify
from .forms import *
from .models import *
from sqlalchemy.exc import SQLAlchemyError  # To catch any errors during the database transaction


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # Fetch all venues from the database
    all_venues = Venue.query.all()

    # Create a dictionary to organize venues by city and state
    data = {}
    for venue in all_venues:
        key = (venue.city, venue.state)
        data.setdefault(key, {'city': venue.city, 'state': venue.state, 'venues': []})
        data[key]['venues'].append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len([show for show in venue.shows if show.start_time > datetime.now()])
        })

    # Convert the dictionary values into a list for rendering
    return render_template('pages/venues.html', areas=list(data.values()))

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: Fix CRSF token
    # Get the search term from the form input (POST request)
    search_term = request.form.get('search_term', '')

    # Perform a case-insensitive search using SQLAlchemy.
    # The ilike() function allows for case-insensitive pattern matching.
    # The '%' symbols are wildcards in SQL, representing any sequence of characters before and after the search term.
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

    # Prepare the response with a list of matching venues.
    # The 'num_upcoming_shows' is assumed to be a property of the Venue model or calculated elsewhere.
    response = {
        "count": len(venues),
        "data": []
    }

    # Populate the 'data' list with matching venue details.
    for venue in venues:
        response['data'].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": venue.num_upcoming_shows  # Assuming num_upcoming_shows is a calculated field
        })

    # Render the results in the template, passing the search term and response.
    return render_template('pages/search_venues.html', results=response, search_term=search_term)
  
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    form = VenueForm()
    # Query the venue by ID
    venue = Venue.query.get(venue_id)

    if venue is None:
        return render_template('errors/404.html'), 404  # If venue not found

    # Collect data to pass to the template (including past/upcoming shows)
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": [ genre for genre in venue.genres ],
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": 0,
        "upcoming_shows_count": 0,
    }
    
    # Query and add past and upcoming shows (assuming a Show model exists)
    past_shows = []
    upcoming_shows = []

    # Assuming a Show model exists and tracks artists, venue, and time
    shows = Show.query.filter_by(venue_id=venue_id).all()

    for show in shows:
        show_data = {
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)  # Convert datetime to string
        }

        if show.start_time < datetime.now():
            past_shows.append(show_data)
        else:
            upcoming_shows.append(show_data)

    data["past_shows"] = past_shows
    data["upcoming_shows"] = upcoming_shows
    data["past_shows_count"] = len(past_shows)
    data["upcoming_shows_count"] = len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data, form=form)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm() 

  if form.validate_on_submit(): 
    try:
      # Create a new Venue object with data from the form
      new_venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        genres=','.join(form.genres.data),  # Convert list of genres to a comma-separated string
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data,
        website_link=form.website_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data
      )

      # Add the new venue to the database session
      db.session.add(new_venue)

      # Commit the changes to the database
      db.session.commit()

      # Flash a success message
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

    except Exception as e:
      # Roll back the session in case of an error
      db.session.rollback()

      # Flash an error message
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed. Error: ' + str(e))

    finally:
      # Close the database session
      db.session.close()

  else:
    # If form validation fails, flash error messages
    for field, errors in form.errors.items():
      for error in errors:
        flash(f"Error in the {field} field: {error}")
        return render_template('forms/new_venue.html', form=form)  # Re-render the form with data

  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>', methods=['POST'])
def delete_venue(venue_id):
    # Check if the request has a _method field and if it equals 'DELETE'
    if request.form.get('_method') == 'DELETE':
        try:
            venue = Venue.query.get(venue_id)

            if not venue:
                return jsonify({'error': 'Venue not found.'}), 404

            db.session.delete(venue)
            db.session.commit()

            return jsonify({'success': 'Venue deleted successfully.'}), 200

        except Exception as e:
            db.session.rollback()
            print(f"Error: {str(e)}")
            return jsonify({'error': 'An error occurred while deleting the venue.'}), 500

        finally:
            db.session.close()

    return jsonify({'error': 'Invalid request method.'}), 405

# TODO: VENUE EDIT

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # Query the database to retrieve all artists
    artists = Artist.query.all()

    # Prepare the data in the format needed by the template
    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })

    # Pass the list of artists to the template
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # Query the artist by ID
    artist = Artist.query.get(artist_id)
    if not artist:
        return render_template('errors/404.html'), 404  # Handle case where artist doesn't exist

    # Query the past and upcoming shows for this artist
    past_shows = []
    upcoming_shows = []
    
    now = datetime.now()
    shows = Show.query.filter_by(artist_id=artist_id).all()

    for show in shows:
        show_data = {
            "venue_id": show.venue_id,
            "venue_name": show.venue_shows.name,  # Accessing related venue via backref
            "venue_image_link": show.venue_shows.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S")  # Formatting the time
        }

        if show.start_time < now:
            past_shows.append(show_data)
        else:
            upcoming_shows.append(show_data)

    # Prepare the data dictionary to pass to the template
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres.split(','),  # Convert genres string to list
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # Query the artist by ID
    artist = Artist.query.get(artist_id)
    
    if not artist:
        return render_template('errors/404.html'), 404  # Handle case where artist doesn't exist

    # Pre-populate the form with the artist data
    form = ArtistForm(
        name=artist.name,
        city=artist.city,
        state=artist.state,
        phone=artist.phone,
        genres=artist.genres.split(','),  # Assuming genres are stored as a comma-separated string
        facebook_link=artist.facebook_link,
        image_link=artist.image_link,
        website_link=artist.website_link,
        seeking_venue=artist.seeking_venue,
        seeking_description=artist.seeking_description
    )

    # Prepare artist data for the template (if needed for displaying alongside the form)
    artist_data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres.split(','),
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link
    }

    return render_template('forms/edit_artist.html', form=form, artist=artist_data)



@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # Get the form data
    form = ArtistForm()

    # Fetch the artist to update by ID
    artist = Artist.query.get(artist_id)
    
    if not artist:
        flash(f"Artist with ID {artist_id} not found.", "danger")
        return redirect(url_for('index'))  # Redirect to homepage or any other page

    # Validate the form submission
    if form.validate_on_submit():
        try:
            # Update artist's attributes with the form data
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.genres = ','.join(form.genres.data)  # Assuming genres are stored as a comma-separated string
            artist.facebook_link = form.facebook_link.data
            artist.image_link = form.image_link.data
            artist.website_link = form.website_link.data
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data

            # Commit the changes to the database
            db.session.commit()
            flash(f'Artist {artist.name} was successfully updated!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while updating artist {artist.name}. Error: {str(e)}', 'danger')
    else:
        # If form validation fails, flash error messages
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in the {field} field: {error}")

        # Re-render the form with the artist data when validation fails
        return render_template('forms/edit_artist.html', form=form, artist=artist)

    # Redirect to the artist's page after updating
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()

  if form.validate_on_submit(): 
    try:
      # Create a new artist instance with data from the form
      new_artist = Artist(
        name=request.form['name'],
        city=request.form['city'],
        state=request.form['state'],
        phone=request.form['phone'],
        genres=request.form.getlist('genre'),  # If you're storing genres as a list
        facebook_link=request.form['facebook_link'],
        image_link=request.form['image_link'],
        website_link=request.form['website_link'],
        seeking_venue=True if request.form.get('seeking_venue') == 'y' else False,
        seeking_description=request.form['seeking_description']
      )

      # Add the new artist to the session
      db.session.add(new_artist)
      # Commit the transaction to save the artist in the database
      db.session.commit()

      # On successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      
    except Exception as e:
      # Roll back the session in case of an error
      db.session.rollback()

      # Flash an error message
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed. Error: ' + str(e))

    finally:
      # Close the database session
      db.session.close()

  else:
    # If form validation fails, flash error messages
    for field, errors in form.errors.items():
      for error in errors:
        flash(f"Error in the {field} field: {error}")
        return render_template('forms/new_artist.html', form=form)  # Re-render the form with data

  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')