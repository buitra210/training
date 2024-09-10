from sanic import Blueprint

from app.apis.books_blueprint import books_bp
from app.apis.example_blueprint import example
from app.apis.authen_blueprint import authen

api = Blueprint.group(example, books_bp, authen)
