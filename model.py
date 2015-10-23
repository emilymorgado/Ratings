"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy

# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)
import correlation
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


    def predict_rating(self, movie_object):
        """Predict user's rating of a movie."""

        other_ratings = movie_object.ratings
        # other_ratings is a list of rating objects where the movie_id is our movie_id

        similarities = [
            (self.similarity(r.user), r.score)
            # tuple with the value of calling similarity on self and the user associated with
            # a rating(r). We're doing this for each rating(r) in our list other_ratings
            for r in other_ratings
        ]
        # similarities = []
        # for r in other_ratings:
        #       similarities.append((self.similarity(r.User), r)) <--- Append a tuple to our list

        similarities.sort(reverse=True)

        # similarities = [(sim, r) for sim, r in similarities if sim > 0]

        if not similarities:
            return None

        pos = sum([sim * score for sim, score in similarities if sim > 0])
        neg = sum([-sim * abs(score-6) for sim, score in similarities if sim < 0])
        denominator = sum([abs(sim) for sim, score in similarities])

        return (pos + neg)/float(denominator)

    def similarity(self, other):
        """Return Pearson rating for user compared to other user."""

        self_ratings = {}
        paired_ratings = []

        for rating_object in self.ratings:
            self_ratings[rating_object.movie_id] = rating_object.score
            #movie_id: score

        for rating_object in other.ratings:
            self_score = self_ratings.get(rating_object.movie_id)
            # checkin if the self_object has a score for the movie_id in this rating_object
            # returns the score if there, else None
            if self_score:
                paired_ratings.append( (float(rating_object.score), float(self_score)) )

        if paired_ratings:
            return correlation.pearson(paired_ratings)

        else:
            return 0.0

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
