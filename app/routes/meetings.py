"""
API routes for Meeting CRUD operations.
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Meeting

meetings_bp = Blueprint('meetings', __name__, url_prefix='/api/meetings')


@meetings_bp.route('', methods=['GET'])
@login_required
def get_meetings():
    """
    Get all meetings for the current user.
    Query parameters:
        - search: Search by title (optional)
        - date: Filter by date (YYYY-MM-DD) (optional)
        - page: Page number for pagination (default: 1)
        - per_page: Items per page (default: 10)
    
    Returns:
        JSON array of meetings
    """
    # Get query parameters
    search = request.args.get('search', '')
    date_filter = request.args.get('date', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Build query
    query = Meeting.query.filter_by(user_id=current_user.id)
    
    # Apply search filter
    if search:
        query = query.filter(Meeting.title.ilike(f'%{search}%'))
    
    # Apply date filter
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Meeting.date) == filter_date)
        except ValueError:
            return jsonify({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400
    
    # Order by date descending
    query = query.order_by(Meeting.date.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    meetings = pagination.items
    
    return jsonify({
        'meetings': [meeting.to_dict() for meeting in meetings],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@meetings_bp.route('/<int:meeting_id>', methods=['GET'])
@login_required
def get_meeting(meeting_id):
    """
    Get a single meeting by ID with notes and attendees.
    
    Returns:
        JSON object with meeting details
    """
    meeting = Meeting.query.get_or_404(meeting_id)
    
    # Check authorization
    if meeting.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(
        meeting.to_dict(include_notes=True, include_attendees=True)
    ), 200


@meetings_bp.route('', methods=['POST'])
@login_required
def create_meeting():
    """
    Create a new meeting.
    
    Expected JSON:
        {
            "title": "Team Standup",
            "description": "Daily standup meeting",
            "date": "2025-10-15T09:00:00",
            "location": "Conference Room A"
        }
    
    Returns:
        JSON object of created meeting
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    # Parse date
    meeting_date = datetime.utcnow()
    if data.get('date'):
        try:
            meeting_date = datetime.fromisoformat(
                data['date'].replace('Z', '+00:00')
            )
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    
    # Create meeting
    meeting = Meeting(
        title=data['title'],
        description=data.get('description', ''),
        date=meeting_date,
        location=data.get('location', ''),
        user_id=current_user.id
    )
    
    try:
        db.session.add(meeting)
        db.session.commit()
        return jsonify(meeting.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to create meeting',
            'details': str(e)
        }), 500


@meetings_bp.route('/<int:meeting_id>', methods=['PUT'])
@login_required
def update_meeting(meeting_id):
    """
    Update an existing meeting.
    
    Expected JSON:
        {
            "title": "Updated Title",
            "description": "Updated description",
            "date": "2025-10-15T09:00:00",
            "location": "New Location"
        }
    
    Returns:
        JSON object of updated meeting
    """
    meeting = Meeting.query.get_or_404(meeting_id)
    
    # Check authorization
    if meeting.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Update fields
    if 'title' in data:
        meeting.title = data['title']
    if 'description' in data:
        meeting.description = data['description']
    if 'location' in data:
        meeting.location = data['location']
    if 'date' in data:
        try:
            meeting.date = datetime.fromisoformat(
                data['date'].replace('Z', '+00:00')
            )
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    
    try:
        db.session.commit()
        return jsonify(meeting.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to update meeting',
            'details': str(e)
        }), 500


@meetings_bp.route('/<int:meeting_id>', methods=['DELETE'])
@login_required
def delete_meeting(meeting_id):
    """
    Delete a meeting.
    
    Returns:
        JSON confirmation message
    """
    meeting = Meeting.query.get_or_404(meeting_id)
    
    # Check authorization
    if meeting.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        db.session.delete(meeting)
        db.session.commit()
        return jsonify({'message': 'Meeting deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to delete meeting',
            'details': str(e)
        }), 500
