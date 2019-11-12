from functools import wraps 
from flask import session, g 

from cms.admin import admin_bp
from cms.admin.models import User
from flask import render_template, request, redirect, url_for, flash


def protected(route_function):
    @wraps(route_function)
    def wrapped_route_function(**kwargs):
        if g.user is None:
            return redirect(url_for('admin.login'))
        return route_function(**kwargs)
    return wrapped_route_function

# actually should be @admin_bp.before_app_request
# test needs to be improved
# @admin_bp.before_app_request
@admin_bp.before_app_request
# @before_app_request
def load_user():
    user_id = session.get('user_id')
    g.user = User.query.get(user_id) if user_id is not None else None

# https://flask.palletsprojects.com/en/1.1.x/quickstart/#http-methods
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        # https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/#queries-in-views
        user = User.query.filter_by(username=username).first()
        check = user.check_password(password)
        if user is None:
            error = 'no user'
        # elif check is None:
        elif not check:
            error = 'no password'
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('admin.content', type='page'))
        flash(error)
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin.login'))
