from flask import Blueprint, render_template, current_app, redirect, session, request, flash, url_for
from flask.ext.security import RegisterForm
from flask.ext.security.registerable import register_user
from flask.ext.security import login_user
from flask_security import current_user, login_required
from flask.ext.social.utils import get_provider_or_404
from flask.ext.social.views import connect_handler

bp = Blueprint('main', __name__)


@bp.route('/', methods=['GET'])
def index():
    """Returns the dashboard interface."""
    return render_template('index.html')

@bp.route('/thanks', methods=['GET'])
def thanks():
    return render_template('thanks.html')


#@bp.route('/register', methods=['GET', 'POST'])
#@bp.route('/register/<provider_id>', methods=['GET', 'POST'])
def register(provider_id=None):
    if current_user.is_authenticated():
        return redirect(request.referrer or '/')

    form = RegisterForm()

    if provider_id:
        provider = get_provider_or_404(provider_id)
        connection_values = session.get('failed_login_connection', None)
    else:
        provider = None
        connection_values = None

    if form.validate_on_submit():
        #ds = current_app.security.datastore
        user = register_user(**form.to_dict())


        # See if there was an attempted social login prior to registering
        # and if so use the provider connect_handler to save a connection
        #connection_values = session.pop('failed_login_connection', None)

        if connection_values:
            connection_values['user_id'] = user.id
            connect_handler(connection_values, provider)

        if login_user(user):
            #ds.commit()
            flash('Account created successfully', 'info')
            return redirect(url_for('.index'))

        return render_template('thanks.html', user=user)

    login_failed = int(request.args.get('login_failed', 0))

    return render_template('security/register_user.html',
                           register_user_form=form,
                           provider=provider,
                           login_failed=login_failed,
                           connection_values=connection_values)


@bp.route('/reconnect', methods=['GET'])
@login_required
def reconnect():
    social = current_app.extensions['social']
    print social.tumblr
    return render_template('reconnect.html',
                           twitter_conn=social.twitter.get_connection(),
                           facebook_conn=social.facebook.get_connection(),
                           tumblr_conn=social.tumblr.get_connection())

