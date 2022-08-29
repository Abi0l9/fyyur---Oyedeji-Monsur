#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.mime import image
from email.policy import default
import json
from os import abort
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from forms import *
from models import *
import sys


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

csrf = CSRFProtect()


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
csrf.init_app(app)
migrate = Migrate(app, db)


# TODO: connect to a local postgresql database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/fyyur'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

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
    # TODO: replace with real venues data.
    data = []
    all_venues_query = Venue.query.all()

    for venue in all_venues_query:
        data.append({
            'city': venue.city,
            'state': venue.state,
            'venue': []
        })
    for venue in all_venues_query:
        curr_time = datetime.now()
        num_upcoming_shows = 0
        shows = Shows.query.filter_by(venue_id=venue.id).all()

        for show in shows:
            if show.start_time > curr_time:
                num_upcoming_shows += 1
        for ven in data:
            if venue.city == ven['city'] and venue.state == ven['state']:
                ven['venue'].append({
                    'id': venue.id,
                    'name': venue.name,
                    'num_upcoming_shows': num_upcoming_shows
                })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    main_query = request.form.get('search_term', '')
    if main_query == '':
        flash('Search query cannot be blank')
        return render_template('pages/venues.html')

    res = Venue.query.filter(Venue.name.like("%"+main_query+"%")).all()
    # print(res)
    response = {
        "count": len(res),
        "data": []
    }

    for venue in res:
        result = {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": 0,
        }
        response["data"].append(result)
        shows = Shows.query.filter_by(venue_id=result["id"]).all()
        for show in shows:
            if show.start_time > datetime.now():
                result["num_upcoming_shows"] += 1

    print(response)
    res = Venue.query.filter(Venue.name.like("%"+main_query+"%")).all()
    response = {
        "count": len(res),
        "data": []
    }

    for venue in res:
        result = {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": 0,
        }
        response["data"].append(result)
        shows = Shows.query.filter_by(venue_id=result["id"]).all()
        for show in shows:
            if show.start_time > datetime.now():
                result["num_upcoming_shows"] += 1

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    all_shows = Shows.query.filter_by(venue_id=venue_id).all()

    venue = Venue.query.get(venue_id)
    list = ''
    for genre in venue.genres:
        list += genre

    new_list = list.split(',')

    upcoming_shows = []
    past_shows = []

    for shows in all_shows:
        some_shows = {
            'artist_id': shows.artist_id,
            'artist_name': shows.artist.name,
            'artist_image_link': shows.artist.image_link,
            'start_time': format_datetime(str(shows.start_time))
        }

        if shows.start_time > datetime.now():

            upcoming_shows.append(some_shows)
        else:
            past_shows.append(some_shows)

    upcoming_len = len(upcoming_shows)
    past_len = len(past_shows)

    data = {
        'id': venue.id,
        'name': venue.name,
        'genres': new_list,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website_link': venue.website_link,
        'facebook_link': venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        "past_shows_count": past_len,
        "upcoming_shows_count": upcoming_len,
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    reged_venues = Venue.query.all()
    for venues in reged_venues:
        if venues.name == request.form['name']:
            db.session.rollback()
            print("Error....Venue has been listed before!")
            flash('Error....Venue has been listed before!')
            return render_template('pages/home.html')

    first_genres = request.form.getlist('genres')
    slicer = slice(3)
    result = ''
    if request.form.get('seeking_talent') == '1':
        result = True
    else:
        result = False
    form = VenueForm(request.form)
    if form.validate():
        try:
            venue = Venue(name=form.name.data, city=form.city.data,
                          state=form.state.data, address=form.address.data, phone=form.phone.data,
                          genres=first_genres[slicer], facebook_link=form.facebook_link.data, image_link=form.image_link.data,
                          website_link=form.website_link.data, seeking_talent=result, seeking_description=form.seeking_description.data)

            db.session.add(venue)
            db.session.commit()
        # TODO: modify data to be the data object returned from db insertion
        # on successful db insert, flash success
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
        # TODO: on unsuccessful db insert, flash an error instead.
        except:

            db.session.rollback()
            flash('An error occurred. Venue ' +
                  request.form['name'] + ' could not be listed.')
            print(sys.exc_info())

        finally:
            db.session.close()
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    venue = Venue.query.get_or_404(venue_id)
    try:
        db.session.delete(venue)
        db.session.commit()
        flash('Venue deleted, successfully!')
    except:
        db.session.rollback()
        flash('Error!!!!.....Unsuccessful')
        print(sys.exc_info())
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/venues.html')


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = db.session.query(Artist.id, Artist.name).all()

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    main_query = request.form.get('search_term', '')
    if main_query == '':
        flash('Search query cannot be blank')
        return render_template('pages/venues.html')
    res = Artist.query.filter(Artist.name.like("%"+main_query+"%")).all()
    # print(res)
    response = {
        "count": len(res),
        "data": []
    }

    for artist in res:
        result = {
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": 0,
        }
        response["data"].append(result)
        shows = Shows.query.filter_by(artist_id=result["id"]).all()
        for show in shows:
            if show.start_time > datetime.now():
                result["num_upcoming_shows"] += 1

    print(response)

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    all_shows = Shows.query.filter_by(artist_id=artist_id).all()
    artist = Artist.query.get_or_404(artist_id)

    list = ''
    for genre in artist.genres:
        list += genre

    new_list = list.split(',')
    print(new_list)

    upcoming_shows = []
    past_shows = []

    for shows in all_shows:
        some_shows = {
            'venue_id': shows.venue_id,
            'venue_name': shows.venue.name,
            'venue_image_link': shows.venue.image_link,
            'start_time': format_datetime(str(shows.start_time))
        }

        if shows.start_time > datetime.now():

            upcoming_shows.append(some_shows)
        else:
            past_shows.append(some_shows)

    upcoming_len = len(upcoming_shows)
    past_len = len(past_shows)

    data = {
        'id': artist.id,
        'name': artist.name,
        'genres': new_list,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website': artist.website_link,
        'facebook_link': artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        "past_shows_count": past_len,
        "upcoming_shows_count": upcoming_len,
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    query = Artist.query.get(artist_id)
    print(query.seeking_venue)
    seeking_result = ''
    if query.seeking_venue == False:
        seeking_result = 'off'
    elif query.seeking_venue == True:
        seeking_result = 'on'

    artist = {
        "id": query.id,
        "name": query.name,
        "genres": query.genres,
        "city": query.city,
        "state": query.state,
        "phone": query.phone,
        "website": query.website_link,
        "facebook_link": query.facebook_link,
        "seeking_venue": query.seeking_venue,
        "seeking_description": query.seeking_description,
        "image_link": query.image_link
    }

    # TODO: populate form with fields from artist with ID <artist_id>

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    seeking_result = ''
    if artist.seeking_venue == False:
        seeking_result = 'off'
    elif artist.seeking_venue == True:
        seeking_result = 'on'

    print(seeking_result)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    first_genres = request.form.getlist('genres')
    slicer = slice(3)
    genres = first_genres[slicer]
    print(genres)
    artist.genres = genres
    artist.facebook_link = request.form['facebook_link']
    artist.image_link = request.form['image_link']
    artist.website_link = request.form['website_link']

    if request.form.get('seeking_venue') == 'on':
        artist.seeking_venue = True
    else:
        artist.seeking_venue = False

    artist.seeking_description = request.form['seeking_description']

    try:
        db.session.commit()
        flash('Artist ' + request.form['name'] +
              ' has been edited Successfully!')
    except:
        if request.form['name'] == '' or request.form['name'] == None:
            flash('Artist name cannot be blank')
        db.session.rollback()
        print(sys.exc_info())
        flash('Artist ' + request.form['name'] + " couldn't be edited!")

    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    query = Venue.query.get(venue_id)
    venue = {
        "id": query.id,
        "name": query.name,
        "genres": query.genres,
        "city": query.city,
        "state": query.state,
        "address": query.address,
        "phone": query.phone,
        "website": query.website_link,
        "facebook_link": query.facebook_link,
        "seeking_talent": query.seeking_talent,
        "seeking_description": query.seeking_description,
        "image_link": query.image_link
    }

    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    seeking_talent = ''
    if venue.seeking_talent == False:
        seeking_talent = 'off'
    elif venue.seeking_talent == True:
        seeking_talent = 'on'

    print(seeking_talent)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    first_genres = request.form.getlist('genres')
    slicer = slice(3)
    genres = first_genres[slicer]
    print(genres)
    venue.genres = genres
    venue.facebook_link = request.form['facebook_link']
    venue.image_link = request.form['image_link']
    venue.website_link = request.form['website_link']

    if request.form.get('seeking_talent') == 'on':
        venue.seeking_talent = True
    else:
        venue.seeking_talent = False

    venue.seeking_description = request.form['seeking_description']

    try:
        db.session.commit()
        flash('Venue ' + request.form['name'] +
              ' has been edited Successfully!')
    except:
        if request.form['name'] == '' or request.form['name'] == None:
            flash('Venue name cannot be blank')
        db.session.rollback()
        print(sys.exc_info())
        flash('Venue ' + request.form['name'] + " couldn't be edited!")

    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # name = request.form['name']

    # city = request.form['city']
    # state = request.form['state']
    # phone = request.form['phone']
    # first_genres = request.form.getlist('genres')
    # slicer = slice(3)
    # genres = first_genres[slicer]
    # print(genres)
    # facebook_link = request.form['facebook_link']
    # image_link = request.form['image_link']
    # website_link = request.form['website_link']
    # if request.form.get('seeking_venue') == '1':
    #     seeking_venue = True
    # else:
    #     seeking_venue = False
    # seeking_description = request.form['seeking_description']
    # all_data = Artist(name=name, city=city, state=state, phone=phone,
    #                   genres=genres, facebook_link=facebook_link, image_link=image_link,
    #                   website_link=website_link, seeking_venue=seeking_venue,
    #                   seeking_description=seeking_description)
    # reged_artist = Artist.query.all()
    reged_artists = Artist.query.all()
    for artist in reged_artists:
        if artist.name == request.form['name']:
            db.session.rollback()
            print("Error....Artist has been listed before!")
            flash('Error....Artist has been listed before!')
            return render_template('pages/home.html')

    first_genres = request.form.getlist('genres')
    slicer = slice(3)
    result = ''
    if request.form.get('seeking_venue') == '1':
        result = True
    else:
        result = False

    form = ArtistForm(request.form)
    if form.validate():
        try:
            artist = Artist(name=form.name.data, city=form.city.data,
                            state=form.state.data, phone=form.phone.data,
                            genres=first_genres[slicer], facebook_link=form.facebook_link.data, image_link=form.image_link.data,
                            website_link=form.website_link.data, seeking_venue=result, seeking_description=form.seeking_description.data)

            db.session.add(artist)
            db.session.commit()

        # TODO: modify data to be the data object returned from db insertion
        # on successful db insert, flash success
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
        # TODO: on unsuccessful db insert, flash an error instead.
        except:
            db.session.rollback()
            flash('An error occurred. Artist ' +
                  request.form['name'] + ' could not be listed.')
            print(sys.exc_info())

        finally:
            db.session.close()
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.

    data = []
    for show in db.session.query(Shows).join(Artist).join(Venue).all():
        data.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        })

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
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    shows = Shows(artist_id=artist_id, venue_id=venue_id,
                  start_time=start_time)

    # on successful db insert, flash success
    try:
        db.session.add(shows)
        db.session.commit()
        flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
        print(sys.exc_info())
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return render_template('pages/shows.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
