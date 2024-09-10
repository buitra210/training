from pymongo import MongoClient
# from sanic_ext.extensions.openapi.openapi import operation
#
# from app.apis.books_blueprint import update_book
from app.constants.mongodb_constants import MongoCollections
from app.models.book import Book
from app.utils.logger_utils import get_logger
from config import MongoDBConfig

logger = get_logger('MongoDB')


class MongoDB:
    def __init__(self, connection_url=None):
        if connection_url is None:
            #connection_url = f'mongodb://{MongoDBConfig.USERNAME}:{MongoDBConfig.PASSWORD}@{MongoDBConfig.HOST}:{MongoDBConfig.PORT}'
            connection_url = MongoDBConfig.CONNECTION_URL
        self.connection_url = connection_url.split('@')[-1]
        self.client = MongoClient(connection_url)
        self.db = self.client[MongoDBConfig.DATABASE]

        self._books_col = self.db[MongoCollections.books]
        self._users_col = self.db[MongoCollections.users]

    def get_books(self, filter_=None, projection=None):
        try:
            if not filter_:
                filter_ = {}
            cursor = self._books_col.find(filter_, projection=projection)
            data = []
            for doc in cursor:
                data.append(Book().from_dict(doc))
            return data
        except Exception as ex:
            logger.exception(ex)
        return []

    def add_book(self, book: Book):
        try:
            inserted_doc = self._books_col.insert_one(book.to_dict())
            return inserted_doc
        except Exception as ex:
            logger.exception(ex)
        return None

    # TODO: write functions CRUD with books
    def get_book(self, book_id):
        try:
            book = self._books_col.find_one({"_id": book_id})
            book = Book().from_dict(book)
            return book
        except Exception as ex:
            logger.exception(ex)
        return None

    def update_book(self, book_id, body):
        try:
            existing_book = self.get_book(book_id)
            if not existing_book:
                return None

            update_result = self._books_col.update_one({"_id": book_id}, {"$set": body})

            if update_result.modified_count > 0:
                return True
            else:
                return False
        except Exception as ex:
            logger.exception(ex)
            return None

    def delete_book(self, book_id):
        try:
            existing_book = self.get_book(book_id)
            if not existing_book:
                return None
            delete_result = self._books_col.delete_one({"_id": book_id})
            if delete_result.deleted_count > 0:
                return True
            else:
                return False
        except Exception as ex:
            logger.exception(ex)
        return None

    def check_user(self, username, password):
        try:
            user = self._users_col.find_one({"username": username, "password": password})
            if user:
                return True
            return False
        except Exception as ex:
            logger.exception(ex)
        return None

    def register_user(self, username, password):
        try:
            self._users_col.insert_one({"username": username, "password": password})
        except Exception as ex:
            logger.exception(ex)

if __name__ == '__main__':
    db = MongoDB()
    data = db.get_books()
    print(data)

    pass