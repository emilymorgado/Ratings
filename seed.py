"""Utility file to seed ratings database from MovieLens data in seed_data/"""


from model import User
from model import Rating
from model import Movie

from model import connect_to_db, db
from server import app
from datetime import datetime


def load_users():
    """Load users from u.user into database."""

    # print "Users"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        user_id, age, gender, occupation, zipcode = row.split("|")
        # print "User Id: {}. Age: {}. Zipcode: {}.".format(user_id, age, zipcode)
        user = User(user_id=user_id,
                    age=age,
                    zipcode=zipcode)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_movies():
    """Load movies from u.item into database."""

    Movie.query.delete()

    for row in open("seed_data/u.item"):
        row = row.rstrip()
        data = row.split("|")
        movie_id = data[0]
        # print "Movie ID: {}".format(movie_id)
        title = data[1][0:-7]
        # print "Title: {}".format(title)
        imdb_url = data[4]
        # print "IMDB URL: {}.".format(imdb_url)
        date = data[2]
        if len(date) > 6:
            # print "normal date: " + date # date format: 01-Jan-1994
            date = datetime.strptime(date, '%d-%b-%Y')
            # print date
            # print type(date)
        else:
            date = None
            # print "{} has messed up data!".format(title)

        movie = Movie(movie_id=movie_id, title=title, 
                      released_at=date, imdb_url=imdb_url)

        db.session.add(movie)

    db.session.commit()



def load_ratings():
    """Load ratings from u.data into database."""

    Rating.query.delete()

    for row in open("seed_data/u.data"):
        row = row.rstrip()
        data = row.split("\t")
        user_id, movie_id, score = data[0:3]
        # print "USER ID: {}. MOVIE ID: {}. SCORE: {}".format(user_id, movie_id, score)

        rating = Rating(user_id=user_id, movie_id=movie_id, 
                        score=score)

        db.session.add(rating)

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_movies()
    load_ratings()
