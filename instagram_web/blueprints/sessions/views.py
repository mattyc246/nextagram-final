from flask import Blueprint, render_template, redirect, url_for, request, flash
from models.user import User
from flask_login import login_user
from instagram_web.util.google_oauth import oauth

sessions_blueprint = Blueprint(
    'sessions', __name__, template_folder='templates/sessions')


@sessions_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('new.html')


@sessions_blueprint.route('/', methods=['POST'])
def create():
    user = User.get_or_none(User.email == request.form.get('email'))

    if not user:
        flash(
            f"No account registered under the email {request.form.get('email')}", 'warning')
        return redirect(url_for('sessions.new'))

    login_user(user)

    flash(f'Welcome back, {user.username}', 'success')
    return redirect(url_for('users.index'))


@sessions_blueprint.route('/google/login', methods=['GET'])
def google_login():
    redirect_uri = url_for('sessions.authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@sessions_blueprint.route('/authorize/google', methods=['GET'])
def authorize():
    token = oauth.google.authorize_access_token()

    if not token:
        flash('Something went wrong, try again later', 'warning')
        return redirect(url_for('home'))

    email = oauth.google.get(
        'https://www.googleapis.com/oauth2/v2/userinfo').json()['email']

    user = User.get_or_none(User.email == email)

    if not user:
        flash(f'No user registered with the email: {email}', 'warning')
        return redirect(url_for('home'))

    login_user(user)
    flash(f'Welcome back {user.username}', 'success')
    return redirect(url_for('users.index'))
