#!/usr/bin/env python

from flask import Flask, Blueprint, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.database import init_db
from app.helpers import return_result
from app.blueprints.classify import classify_blueprint
from app.blueprints.recipes import recipes_blueprint

application = Flask(__name__)
CORS(application)
# limiter = Limiter(
#     application,
#     key_func=get_remote_address,
#     default_limits=["40 per day", "20 per hour"]
# )

init_db()


application.register_blueprint(recipes_blueprint, url_prefix='/api/recipes')
application.register_blueprint(classify_blueprint, url_prefix='/api/classify')


@application.errorhandler(500)
def server_error(e):
    return return_result(code=500, status="error", message=str(e))


if __name__ == '__main__':
    application.run()
