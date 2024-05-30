import click
from flask import current_app, g
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

def get_db():
    if 'db' not in g:
        # Create SQLAlchemy engine
        engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])

        # Create scoped session
        db_session = scoped_session(sessionmaker(bind=engine))

        # Store session in Flask's application context
        g.db = db_session

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        # Close SQLAlchemy session
        db.remove()

def init_db():
    db = get_db()

    # Create all tables defined in SQLAlchemy models
    db.create_all()
    print("Database initialized successfully.")

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """Register database functions with the Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
