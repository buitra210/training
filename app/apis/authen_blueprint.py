import os
import sys
from crypt import methods

import jwt
from pymongo.message import query
from sanic_ext import  openapi, validate
from app.constants.cache_constants import CacheConstants
from app.databases.mongodb import MongoDB
from app.models.auth import AuthBase, AuthQuery
from app.utils.jwt_utils import generate_jwt
from config import Config

cwd = os.path.dirname(os.path.abspath(__file__))
prj_dir = os.path.join(cwd, os.pardir, os.pardir)
print(cwd)
print(prj_dir)
sys.path.append(prj_dir)

import uuid
# from crypt import methods

from sanic import Blueprint, BadRequest, Unauthorized
from sanic.response import json

# from app.constants.cache_constants import CacheConstants
#from app.databases.mongodb import MongoDB
# from app.databases.redis_cached import get_cache, set_cache
#from app.decorators.json_validator import validate_with_jsonschema
#from app.hooks.error import ApiInternalError
#from app.models.book import create_book_json_schema, Book
from app.databases.redis_cached import get_cache, set_cache

authen = Blueprint('authen_blueprint', url_prefix='/authen')
_db = MongoDB()


# @authen.route('/register', methods={'POST'})
# @openapi.parameter(name='username', description='Name of user', location='query', required=True)
# @openapi.parameter(name='password', location='query', required=True)
# @openapi.parameter(name='role',location='query', required=True)
# @validate(query=AuthBase)
# async def login(request, query:AuthBase):
#     try:
#         results = generate_jwt(
#             username=query.username, role=query.role, password=query.password
#         )
#     except ValueError:
#         raise BadRequest('Login Fail')
#
#     return json({
#         'jwt': results,
#         'role': query.role
#     })


@authen.route('/register', methods={'POST'})
@openapi.parameter(name='username', description='Name of user', location='query', required=True)
@openapi.parameter(name='password', location='query', required=True)
@validate(query=AuthBase)
async def register(request, query:AuthBase):
   if query.username and query.password:
       _db.register_user(query.username, query.password)
       return json({
           'message': 'Register success'
       })
   else:
        raise BadRequest('Register Fail')

@authen.route('/login', methods={'GET'})
@openapi.parameter(name='username', description='Name of user', location='query', required=True)
@openapi.parameter(name='password', location='query', required=True)
@validate(query=AuthBase)
async def login(request, query:AuthBase):
    if _db.check_user(query.username, query.password):
        try:
            results = generate_jwt(
                username=query.username,  password=query.password
            )
        except ValueError:
            raise BadRequest('Login Fail')

        return json({
            'jwt': results,
            'role': 'user'
        })

    else:
        raise Unauthorized('Login Fail')

# @authen.route('/check-user', methods={'GET'})
# @openapi.summary("Check user is admin or not")
# @openapi.parameter(name='jwt', description='JWT', location='query', required=True)
# @validate(query=AuthQuery)
# async def check_user(request, query: AuthQuery):
#     token = query.jwt
#     try:
#         jwt_ = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
#     except jwt.exceptions.InvalidTokenError:
#         raise Unauthorized(message="Signature verification failed")
#
#     return json(jwt_)
