"""
Main routes for rendering templates.
"""
from flask import Blueprint, render_template
from flask_login import login_required

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def index():
    """Home page - displays all meetings."""
    return render_template('index.html')


@main_bp.route('/meeting/<int:meeting_id>')
@login_required
def meeting_detail(meeting_id):
    """Meeting detail page - shows notes and attendees."""
    return render_template('meeting_detail.html', meeting_id=meeting_id)
