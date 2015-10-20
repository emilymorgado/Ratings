"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy

# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)


# Put your Movie and Rating model classes here.

class Movie(db.Model):
    """Movie in Ratings website"""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(75), nullable=False)
    released_at = db.Column(db.DateTime, nullable=True)
    imdb_url = db.Column(db.String(100), nullable=True)


    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<Movie movie_id={} title={}>".format(self.movie_id, self.title)


class Rating(db.Model):
    """Rating in ratings website"""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, primary_key=True, nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref=db.backref('ratings'))
    movie = db.relationship('Movie', backref=db.backref('ratings'))

    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<Rating rating_id={} movie_id={}>".format(self.rating_id, self.movie_id)



##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ratings.db'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
