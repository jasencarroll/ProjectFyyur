import logging
from logging import Formatter, FileHandler
from flask import (
    Flask, 
    json,
    render_template, 
    request,
    Response,
    flash,
    redirect,
    url_for
)
from app import app, db
from .forms import *
from .models import *


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
    form = VenueForm()
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
    return render_template('pages/venues.html', areas=list(data.values()), form=form)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    form = VenueForm()
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
            #"num_upcoming_shows": venue.num_upcoming_shows  # Assuming num_upcoming_shows is a calculated field
        })

    # Render the results in the template, passing the search term and response.
    return render_template('pages/search_venues.html', results=response, search_term=search_term, form=form)
  
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    form = VenueForm(request.form)
    # Query the venue by ID
    venue = Venue.query.get(venue_id)

    if venue is None:
        return render_template('errors/404.html'), 404  # If venue not found

    # Collect data to pass to the template (including past/upcoming shows)
    data = vars(venue)
    
    # Query and add past and upcoming shows (assuming a Show model exists)
    past_shows = []
    upcoming_shows = []

    # Assuming a Show model exists and tracks artists, venue, and time
    shows = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).all()

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
        genres=form.genres.data,  # Convert list of genres to a comma-separated string
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
            # Query the venue from the database using the venue_id
            venue = Venue.query.get(venue_id)

            # If the venue does not exist, flash an error message and redirect to the venue page
            if not venue:
                flash('Venue not found.', 'danger')
                return redirect(url_for('show_venue', venue_id=venue_id))
            
            # Delete all shows associated with the artist
            shows = Show.query.filter_by(venue_id=venue_id).all()
            for show in shows:
                db.session.delete(show)

            # Delete the venue from the database
            db.session.delete(venue)
            db.session.commit()

            # Flash a success message and redirect to the venues page after deletion
            flash('Venue deleted successfully.', 'success')
            return redirect(url_for('venues'))

        except Exception as e:
            # If there's an error, rollback the session and flash an error message
            db.session.rollback()
            flash('An error occurred while deleting the venue.', 'danger')
            print(f"Error: {str(e)}")
            # Redirect back to the individual venue page if there's an error
            return redirect(url_for('show_venue', venue_id=venue_id))

        finally:
            # Ensure the session is closed after the operation
            db.session.close()

    # If the request method is not 'DELETE', flash an error message and reload the page
    flash('Invalid request method.', 'danger')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    form = ArtistForm()
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
    return render_template('pages/artists.html', artists=data, form=form)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    form = ArtistForm()
    # Get the search term from the form input
    search_term = request.form.get('search_term', '')

    # Perform a case-insensitive search using ilike
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

    # Prepare the response
    response = {
        "count": len(artists),
        "data": []
    }

    # Populate the response data with artists matching the search
    for artist in artists:
        response['data'].append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(artist.shows)  # Assuming the relationship 'shows' is defined in Artist
        })

    # Render the search results template
    return render_template('pages/search_artists.html', results=response, search_term=search_term, form=form)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    form = ArtistForm()
    # Query the artist by ID
    artist = Artist.query.get(artist_id)
    if not artist:
        return render_template('errors/404.html'), 404  # Handle case where artist doesn't exist

    data = vars(artist)
    
    # Query the past and upcoming shows for this artist
    past_shows = []
    upcoming_shows = []
    
    now = datetime.now()
    shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).all()

    for show in shows:
        show_data = {
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,  # Accessing related venue via backref
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S")  # Formatting the time
        }

        if show.start_time < now:
            past_shows.append(show_data)
        else:
            upcoming_shows.append(show_data)
    data["past_shows"] = past_shows
    data["upcoming_shows"] = upcoming_shows
    data["past_shows_count"] = len(past_shows)
    data["upcoming_shows_count"] = len(upcoming_shows)
    
    return render_template('pages/show_artist.html', artist=data, form=form)
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
        genres=artist.genres,  # Assuming genres are stored as a comma-separated string
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
        "genres": artist.genres,
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
            artist.genres = form.genres.data  # Assuming genres are stored as a comma-separated string
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
    # Query the venue by ID
    venue = Venue.query.get(venue_id)
    
    if not venue:
        flash(f"Venue with ID {venue_id} not found.", "danger")
        return redirect(url_for('index'))  # Redirect to homepage or any other page

    # Pre-populate the form with the venue's data
    form = VenueForm(
        name=venue.name,
        genres=venue.genres,  # Assuming genres are stored as a comma-separated string
        address=venue.address,
        city=venue.city,
        state=venue.state,
        phone=venue.phone,
        website=venue.website_link,
        facebook_link=venue.facebook_link,
        seeking_talent=venue.seeking_talent,
        seeking_description=venue.seeking_description,
        image_link=venue.image_link
    )

    # Prepare the venue data to pass to the template
    venue_data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,  # Convert genres string to a list
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
    }

    return render_template('forms/edit_venue.html', form=form, venue=venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # Get the form data
    form = VenueForm()

    # Fetch the venue by ID
    venue = Venue.query.get(venue_id)

    if not venue:
        flash(f"Venue with ID {venue_id} not found.", "danger")
        return redirect(url_for('index'))  # Redirect to homepage or any other page

    # Validate the form submission
    if form.validate_on_submit():
        try:
            # Update the venue's attributes with the form data
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.phone = form.phone.data
            venue.genres = form.genres.data  # Assuming genres are stored as a comma-separated string
            venue.facebook_link = form.facebook_link.data
            venue.image_link = form.image_link.data
            venue.website_link = form.website_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data

            # Commit the changes to the database
            db.session.commit()
            flash(f'Venue {venue.name} was successfully updated!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while updating the venue. Error: {str(e)}', 'danger')

    else:
        # Flash form validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in the {field} field: {error}", "danger")
        # Re-render the form with the current data
        return render_template('forms/edit_venue.html', form=form, venue=venue)

    # Redirect to the venue's page after updating
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
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        genres=form.genres.data,  # Convert list of genres to a comma-separated string
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data,
        website_link=form.website_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data
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

#  Delete Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>', methods=['POST'])
def delete_artist(artist_id):
    # Check if the request has a _method field and if it equals 'DELETE'
    if request.form.get('_method') == 'DELETE':
        try:
            # Query the artist from the database using the artist_id
            artist = Artist.query.get(artist_id)

            # If the artist does not exist, return a flash message and redirect to the artist page
            if not artist:
                flash('Artist not found.', 'danger')
                return redirect(url_for('show_artist', artist_id=artist_id))

            # Delete all shows associated with the artist
            shows = Show.query.filter_by(artist_id=artist_id).all()
            for show in shows:
                db.session.delete(show)
                
            # Delete the artist from the database
            db.session.delete(artist)
            db.session.commit()

            # Flash a success message and redirect to the artists page after deletion
            flash('Artist deleted successfully.', 'success')
            return redirect(url_for('artists'))

        except Exception as e:
            # If there's an error, rollback the session and flash an error message
            db.session.rollback()
            flash('An error occurred while deleting the artist.', 'danger')
            print(f"Error: {str(e)}")
            # Redirect back to the individual artist page if there's an error
            return redirect(url_for('show_artist', artist_id=artist_id))

        finally:
            # Ensure the session is closed after the operation
            db.session.close()

    # If the request method is not 'DELETE', flash an error message and reload the page
    flash('Invalid request method.', 'danger')
    return redirect(url_for('show_artist', artist_id=artist_id))
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # Query all shows from the database
    shows = Show.query.join(Venue).join(Artist).all()

    # Prepare the data for each show
    data = []
    for show in shows:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,  # Access related venue name
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,  # Access related artist name
            "artist_image_link": show.artist.image_link,  # Access artist image link
            "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S")  # Format start time
        })

    # Render the template with the shows data
    return render_template('pages/shows.html', shows=data)
  
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # Instantiate the form with the POST data
    form = ShowForm()

    # Validate the form submission
    if form.validate_on_submit():
        try:
            # Create a new Show record using form data
            new_show = Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data
            )
            
            # Add the new show to the database session and commit
            db.session.add(new_show)
            db.session.commit()

            # On successful db insert, flash success
            flash('Show was successfully listed!', 'success')
        except Exception as e:
            # On unsuccessful db insert, rollback and flash an error message
            db.session.rollback()
            flash(f'An error occurred. Show could not be listed. Error: {str(e)}', 'danger')
    else:
        # Flash form validation errors if form is invalid
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in the {field} field: {error}", 'danger')

    # Redirect to the home page or render the home page after the operation
    return redirect(url_for('index'))  # Or return render_template('pages/home.html') if you want to stay on the home page

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