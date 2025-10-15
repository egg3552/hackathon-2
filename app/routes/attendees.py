"""
API routes for Attendee CRUD operations.
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Attendee, Meeting

attendees_bp = Blueprint('attendees', __name__, url_prefix='/api/attendees')


@attendees_bp.route('', methods=['GET'])
@login_required
def get_attendees():
    """
    Get all attendees for a specific meeting.
    Query parameters:
        - meeting_id: Meeting ID (required)
    
    Returns:
        JSON array of attendees
    """
    meeting_id = request.args.get('meeting_id', type=int)
    
    if not meeting_id:
        return jsonify({'error': 'meeting_id is required'}), 400
    
    # Verify meeting exists and user owns it
    meeting = Meeting.query.get_or_404(meeting_id)
    if meeting.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    attendees = Attendee.query.filter_by(meeting_id=meeting_id)\
        .order_by(Attendee.name).all()
    
    return jsonify({
        'attendees': [attendee.to_dict() for attendee in attendees]
    }), 200


@attendees_bp.route('/<int:attendee_id>', methods=['GET'])
@login_required
def get_attendee(attendee_id):
    """
    Get a single attendee by ID.
    
    Returns:
        JSON object with attendee details
    """
    attendee = Attendee.query.get_or_404(attendee_id)
    
    # Check authorization
    if attendee.meeting.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(attendee.to_dict()), 200


@attendees_bp.route('', methods=['POST'])
@login_required
def create_attendee():
    """
    Create a new attendee for a meeting.
    
    Expected JSON:
        {
            "meeting_id": 1,
            "name": "John Doe",
            "email": "john@example.com"
        }
    
    Returns:
        JSON object of created attendee
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('meeting_id') or not data.get('name') \
            or not data.get('email'):
        return jsonify({
            'error': 'meeting_id, name, and email are required'
        }), 400
    
    # Verify meeting exists and user owns it
    meeting = Meeting.query.get_or_404(data['meeting_id'])
    if meeting.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Create attendee
    attendee = Attendee(
        name=data['name'],
        email=data['email'],
        meeting_id=data['meeting_id']
    )
    
    try:
        db.session.add(attendee)
        db.session.commit()
        return jsonify(attendee.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to create attendee',
            'details': str(e)
        }), 500


@attendees_bp.route('/<int:attendee_id>', methods=['PUT'])
@login_required
def update_attendee(attendee_id):
    """
    Update an existing attendee.
    
    Expected JSON:
        {
            "name": "Updated Name",
            "email": "updated@example.com"
        }
    
    Returns:
        JSON object of updated attendee
    """
    attendee = Attendee.query.get_or_404(attendee_id)
    
    # Check authorization
    if attendee.meeting.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        attendee.name = data['name']
    if 'email' in data:
        attendee.email = data['email']
    
    try:
        db.session.commit()
        return jsonify(attendee.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to update attendee',
            'details': str(e)
        }), 500


@attendees_bp.route('/<int:attendee_id>', methods=['DELETE'])
@login_required
def delete_attendee(attendee_id):
    """
    Delete an attendee.
    
    Returns:
        JSON confirmation message
    """
    attendee = Attendee.query.get_or_404(attendee_id)
    
    # Check authorization
    if attendee.meeting.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        db.session.delete(attendee)
        db.session.commit()
        return jsonify({'message': 'Attendee deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to delete attendee',
            'details': str(e)
        }), 500
