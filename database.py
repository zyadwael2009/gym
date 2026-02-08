"""Database initialization and migration commands"""
from flask import Flask, current_app
from flask.cli import with_appcontext
from flask_migrate import init, migrate, upgrade
from app.database import db
import click

def init_db():
    """Initialize database"""
    db.create_all()
    print("Database initialized.")

@click.command()
@with_appcontext
def create_tables():
    """Create database tables"""
    db.create_all()
    print("Database tables created.")

@click.command()
@with_appcontext
def drop_tables():
    """Drop all database tables"""
    db.drop_all()
    print("Database tables dropped.")

@click.command()
@with_appcontext
def reset_db():
    """Reset database (drop and create)"""
    db.drop_all()
    db.create_all()
    print("Database reset completed.")

# Register commands
def register_cli_commands(app):
    """Register CLI commands with Flask app"""
    app.cli.add_command(create_tables)
    app.cli.add_command(drop_tables)
    app.cli.add_command(reset_db)
