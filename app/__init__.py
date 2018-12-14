from flask import Flask
from flask_cors import CORS

from app.database import init_db
from app.helpers import return_result
from app.blueprints.classify import classify_blueprint
from app.blueprints.recipes import recipes_blueprint

application = Flask(__name__)
CORS(application)

init_db()


application.register_blueprint(recipes_blueprint, url_prefix='/api/recipes')
application.register_blueprint(classify_blueprint, url_prefix='/api/classify')


@application.errorhandler(500)
def server_error(e):
    return return_result(code=500, status="error", message=str(e))
