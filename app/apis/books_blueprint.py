import sys
import os

cwd = os.path.dirname(os.path.abspath(__file__))
prj_dir = os.path.join(cwd, os.pardir, os.pardir)
print(cwd)
print(prj_dir)
sys.path.append(prj_dir)

import uuid
# from crypt import methods

from sanic import Blueprint
from sanic.response import json

# from app.constants.cache_constants import CacheConstants
from app.databases.mongodb import MongoDB
# from app.databases.redis_cached import get_cache, set_cache
from app.decorators.json_validator import validate_with_jsonschema
from app.hooks.error import ApiInternalError
from app.models.book import create_book_json_schema, Book

books_bp = Blueprint('books_blueprint', url_prefix='/books')

_db = MongoDB()


@books_bp.route('/')
async def get_all_books(request):
    # # TODO: use cache to optimize api
    # async with request.app.ctx.redis as r:
    #     books = await get_cache(r, CacheConstants.all_books)
    #     if books is None:
    #         book_objs = _db.get_books()
    #         books = [book.to_dict() for book in book_objs]
    #         await set_cache(r, CacheConstants.all_books, books)

    book_objs = _db.get_books()
    books = [book.to_dict() for book in book_objs]
    number_of_books = len(books)
    return json({
        'n_books': number_of_books,
        'books': books
    })


@books_bp.route('/', methods={'POST'})
# @protected  # TODO: Authenticate
@validate_with_jsonschema(create_book_json_schema)  # To validate request body
async def create_book(request, username=None):
    body = request.json

    book_id = str(uuid.uuid4())
    book = Book(book_id).from_dict(body)
    book.owner = username
    # # TODO: Save book to database
    inserted = _db.add_book(book)
    if not inserted:
        raise ApiInternalError('Fail to create book')

    # TODO: Update cache

    return json({'status': 'success'})


# TODO: write api get, update, delete book

@books_bp.route('/<book_id>', methods={'GET'})
async def get_book(request, book_id, username=None):
    book = _db.get_book(book_id)

    if not book:
        return json({'error': 'Book not found'}, status=404)

    book = book.to_dict()
    return json({
        'book': book
    })

@books_bp.route('/<book_id>', methods={'PUT'})
async def update_book(request, book_id, username=None):
    body = request.json

    update_result = _db.update_book(book_id, body)

    if update_result is False:
        raise ApiInternalError('Fail to update book')
    elif update_result is None:
        return json({'error': 'Book not found'}, status=404)

    return json({'message': 'Book updated successfully'}, status=200)

@books_bp.route('/<book_id>', methods={'DELETE'})
async def delete_book(request, book_id, username=None):
    delete_result = _db.delete_book(book_id)

    if delete_result is None:
        raise ApiInternalError('Fail to delete book')
    elif delete_result is False:
        return json({'error': 'Book not found'}, status=404)

    return json({'message': 'Book deleted successfully'}, status=200)