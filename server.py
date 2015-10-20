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
        return redirect('/')
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



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()