"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

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

    return render_template("create_account.html")


@app.route("/new_account", methods=["POST"])
def check_new_account():

    email = request.form.get("email")
    password = request.form.get("password")

    existing_account = User.query.filter(User.email == email).first()

    if (not existing_account) and (len(password) > 0):
        flash("Your account has been created!")
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    elif existing_account:
        flash("That account already exists")
        return redirect('/sign-up-form')
    else:
        flash("You need a password.")
        return redirect('/sign-up-form')





if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()