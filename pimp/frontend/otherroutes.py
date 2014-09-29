from flask import Blueprint, render_template

bp = Blueprint('other', __name__)


@bp.route('/other', methods=['GET'])
def index():
    """Returns the dashboard interface."""
    return render_template('index.html')