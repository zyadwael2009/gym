# Flask Gym Management System

This is a multi-branch gym management system built with Flask. 

## Project Structure
- Flask application with blueprints for modular organization
- SQLAlchemy ORM for database operations
- JWT-based authentication with role-based access control
- Subscription management with payment integration
- Customer health tracking and attendance monitoring
- Administrative dashboards for different user roles

## Tech Stack
- Flask with Flask-RESTful/Blueprints
- SQLAlchemy ORM with PostgreSQL/SQLite
- Flask-JWT-Extended for authentication
- Flask-Migrate for database migrations
- Jinja2 for test page templates

## Development Guidelines
- Keep business logic in service layer, not in routes
- Use decorators for authentication and authorization
- Return JSON responses for APIs
- Test pages are for manual API testing only
- Follow clean architecture principles