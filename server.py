"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from datetime import datetime

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/sign-up-form")
def show_signup_form():
    """Show sign up form"""

    return render_template("create_account.html")


@app.route("/new-account", methods=["POST"])
def check_new_account():
    """Check if new account already exsists and has password"""

    email = request.form.get("email")
    password = request.form.get("password")

    existing_account = User.query.filter(User.email == email).first()

    if (not existing_account) and (len(password) > 0):
        flash("Your account has been created!")
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        session["user_email"] = email
        print session["user_email"]
        return redirect('/')
    elif existing_account:
        flash("That account already exists")
        return redirect('/sign-up-form')
    else:
        flash("You need a password.")
        return redirect('/sign-up-form')


@app.route("/check-login", methods=["POST"])
def check_login():
    """check that login info is correct"""

    email = request.form.get("email")
    password = request.form.get("password")

    existing_account = User.query.filter(User.email == email, 
                                         User.password == password).first()

    if existing_account:
        flash("You have been logged in.")
        session["user_email"] = email
        print session["user_email"]
        url = '/users/' + str(existing_account.user_id)
        return redirect(url)
    else:
        flash("Email or password invalid.")
        return redirect('/login')


@app.route("/login")
def login_page():
    """log in user"""

    return render_template("login.html")


@app.route("/logout")
def logout():
    """log user out"""
    session.clear()
    flash("You've been logged out!")
    return redirect('/')


@app.route("/users/<int:user_id>")
def make_user_page(user_id):
    """generates user profile page"""
    user_info = User.query.get(user_id);
    user_ratings = db.session.query(Rating.score, Movie.title).join(Movie).filter(Rating.user_id == user_id).all()
    return render_template("user_profile.html", user_info=user_info, user_ratings=user_ratings)


@app.route('/movies')
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.title).all()
    return render_template("movie_list.html", movies=movies)

@app.route('/movies/<int:movie_id>')
def make_movie_page(movie_id):
    """generates movie info page"""

    # this grabs the row from the Movie Table and the released_at field
    movie_info = Movie.query.get(movie_id);
    movie_release = movie_info.released_at
    movie_release = movie_release.strftime("%A, %B %d, %Y")
    # movie_ratings = the score and user_id for the movie_id
    movie_ratings = db.session.query(Rating.score, Rating.user_id).filter(Rating.movie_id == movie_id).all()
    # if the session has a user, grab the user's score from the Rating table
    scores = [score for score, user_id in movie_ratings]
    avg_rating = float(sum(scores))/len(scores)
    avg_rating = "{:.2f}".format(avg_rating)


    # TODO! We could change this to user_id
    if session.get("user_email"):
        email = session["user_email"]
        rated = (db.session.query(Rating.score).join(User)
                 .filter(Rating.movie_id == movie_id, User.email == email)
                 .first())
        if rated:
            effective_rating = rated[0]
            prediction = False
        else:
            user = User.query.filter(User.email == email).first()
            prediction = user.predict_rating(movie_info)
            effective_rating = prediction
        # else it hasn't been rated
    #they are not logged in
    else:
        rated = False
        prediction = False
        effective_rating = False


    the_eye = User.query.filter_by(email="the-eye@of-judgment.com").first()
    eye_rating = Rating.query.filter(
            Rating.user_id == the_eye.user_id, Rating.movie_id == movie_info.movie_id).first()

    if eye_rating is None:
        eye_rating = the_eye.predict_rating(movie_info)

    else:
        eye_rating = eye_rating.score

    if eye_rating and effective_rating:
        difference = abs(eye_rating - effective_rating)

    else:
        # We couldn't get an eye rating, so we'll skip difference
        difference = None

    BERATEMENT_MESSAGES = [
           "I suppose you don't have such bad taste after all.",
           "I regret every decision that I've ever made that has brought me" +
               " to listen to your opinion.",
           "Words fail me, as your taste in movies has clearly failed you.",
           "That movie is great. For a clown to watch. Idiot.",
           "Words cannot express the awfulness of your taste."
       ]

    if difference:
        beratement = BERATEMENT_MESSAGES[int(difference)]

    else:
        beratement = None


    return render_template("movie_profile.html", movie_release=movie_release, 
                                                 movie_info=movie_info, 
                                                 movie_ratings=movie_ratings, 
                                                 rated=rated,
                                                 average=avg_rating,
                                                 prediction=prediction,
                                                 beratement=beratement)


@app.route('/movies/<int:movie_id>/rate', methods=["GET"])
def rate_movie(movie_id):
    """adds rating to database"""

    # score is taken from the form and turned into an int
    score = request.args.get('score')
    score = int(score)

    # this grabs the email from the User table that matches the email from the Flask session
    # this binds user_id to the user_id from the User table
    user = User.query.filter(User.email == session["user_email"]).first()
    user_id = user.user_id

    # this grabs the current score from the Rating table and binds it to user_score
    user_score = (db.session.query(Rating.score).filter(Rating.user_id == user_id, 
                                                Rating.movie_id == movie_id).first())

    # if the user_score (from the Rating Table) matches the input score, do nothing
    #FIX THIS TO NOT REPLACE ALL THE DATABASE
    if user_score:
        db.session.query(Rating).filter(Rating.user_id == user_id, 
                                        Rating.movie_id == movie_id).update({Rating.score: score})
        db.session.commit()
        # This adds a new rating to the Rating table in the db (score comes from the form)
    else:
        rating = Rating(movie_id=movie_id, user_id=user_id, score=score)
        print rating
        db.session.add(rating)
        db.session.commit()

    url = "/movies/" + str(movie_id)
    return redirect(url)



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()