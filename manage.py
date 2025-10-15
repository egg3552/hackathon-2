"""
Application entry point for running the Flask app.
Used for local development and Heroku deployment.
"""
import os
from app import create_app, db
from app.models import User, Meeting, Note, Attendee

# Create Flask application instance
app = create_app(os.getenv('FLASK_ENV') or 'default')


@app.shell_context_processor
def make_shell_context():
    """
    Make database and models available in Flask shell.
    Usage: flask shell
    """
    return {
        'db': db,
        'User': User,
        'Meeting': Meeting,
        'Note': Note,
        'Attendee': Attendee
    }


@app.cli.command()
def initdb():
    """
    Initialize the database.
    Usage: flask initdb
    """
    db.create_all()
    print('Database initialized.')


@app.cli.command()
def dropdb():
    """
    Drop all database tables.
    Usage: flask dropdb
    """
    db.drop_all()
    print('Database dropped.')


if __name__ == '__main__':
    app.run(debug=True)
