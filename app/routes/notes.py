"""
API routes for Note CRUD operations.
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Note, Meeting

notes_bp = Blueprint('notes', __name__, url_prefix='/api/notes')


@notes_bp.route('', methods=['GET'])
@login_required
def get_notes():
    """
    Get all notes for a specific meeting.
    Query parameters:
        - meeting_id: Meeting ID (required)
    
    Returns:
        JSON array of notes
    """
    meeting_id = request.args.get('meeting_id', type=int)
    
    if not meeting_id:
        return jsonify({'error': 'meeting_id is required'}), 400
    
    # Verify meeting exists and user owns it
    meeting = Meeting.query.get_or_404(meeting_id)
    if meeting.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notes = Note.query.filter_by(meeting_id=meeting_id)\
        .order_by(Note.created_at.desc()).all()
    
    return jsonify({
        'notes': [note.to_dict() for note in notes]
    }), 200


@notes_bp.route('/<int:note_id>', methods=['GET'])
@login_required
def get_note(note_id):
    """
    Get a single note by ID.
    
    Returns:
        JSON object with note details
    """
    note = Note.query.get_or_404(note_id)
    
    # Check authorization
    if note.meeting.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(note.to_dict()), 200


@notes_bp.route('', methods=['POST'])
@login_required
def create_note():
    """
    Create a new note for a meeting.
    
    Expected JSON:
        {
            "meeting_id": 1,
            "content": "Meeting notes content (supports Markdown)"
        }
    
    Returns:
        JSON object of created note
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('meeting_id') or not data.get('content'):
        return jsonify({'error': 'meeting_id and content are required'}), 400
    
    # Verify meeting exists and user owns it
    meeting = Meeting.query.get_or_404(data['meeting_id'])
    if meeting.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Create note
    note = Note(
        content=data['content'],
        meeting_id=data['meeting_id']
    )
    
    try:
        db.session.add(note)
        db.session.commit()
        return jsonify(note.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to create note',
            'details': str(e)
        }), 500


@notes_bp.route('/<int:note_id>', methods=['PUT'])
@login_required
def update_note(note_id):
    """
    Update an existing note.
    
    Expected JSON:
        {
            "content": "Updated note content"
        }
    
    Returns:
        JSON object of updated note
    """
    note = Note.query.get_or_404(note_id)
    
    # Check authorization
    if note.meeting.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Update content
    if 'content' in data:
        note.content = data['content']
    
    try:
        db.session.commit()
        return jsonify(note.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to update note',
            'details': str(e)
        }), 500


@notes_bp.route('/<int:note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    """
    Delete a note.
    
    Returns:
        JSON confirmation message
    """
    note = Note.query.get_or_404(note_id)
    
    # Check authorization
    if note.meeting.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        db.session.delete(note)
        db.session.commit()
        return jsonify({'message': 'Note deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to delete note',
            'details': str(e)
        }), 500
