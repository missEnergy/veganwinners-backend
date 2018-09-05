import json
import logging
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from flask import Flask, Blueprint, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app import config
from app.clarifai import has_food, forbidden_ingredients, vegi_ingredients_used
from app.custom_logger import setup_logger
from app.database import db_session, clear_sessions
from app.database import db_session, init_db
from app.helpers import return_result
from app.helpers import return_result

logger = logging.getLogger()
logger.handlers = []
setup_logger(logger)

app = Flask(__name__)
CORS(app)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["40 per day", "20 per hour"]
)

init_db()

recipes_blueprint = Blueprint('recipes', __name__)
classify_blueprint = Blueprint('classify', __name__)


@recipes_blueprint.route('/', methods=['GET'])
@limiter.exempt
def get_all_recipes():
    recipes = Recipe.query

    data = [{
        "id": recipe.id,
        "title": recipe.title,
        "instructions": recipe.instructions,
        "img": recipe.img,
        "type": recipe.type,
        "time": recipe.time,
        "people": recipe.people,
        "owner": recipe.owner,
        "ingredients": [dict([("id", ingredient.id), ("item", ingredient.item), ("quantity", ingredient.quantity)])
                        for ingredient in recipe.ingredients]
    } for recipe in recipes]

    data = sorted(data, key=lambda x: x.get('id'), reverse=True)

    clear_sessions()

    return return_result(data=data)


@recipes_blueprint.route('/approved', methods=['GET'])
@limiter.exempt
def get_all_recipes_approved():
    recipes = Recipe.query.filter(Recipe.approved)

    data = [{
        "id": recipe.id,
        "title": recipe.title,
        "instructions": recipe.instructions,
        "img": recipe.img,
        "type": recipe.type,
        "time": recipe.time,
        "people": recipe.people,
        "owner": recipe.owner,
        "ingredients": [dict([("id", ingredient.id), ("item", ingredient.item), ("quantity", ingredient.quantity)])
                        for ingredient in recipe.ingredients]
    } for recipe in recipes]

    data = sorted(data, key=lambda x: x.get('id'), reverse=True)

    clear_sessions()

    return return_result(data=data)


@recipes_blueprint.route('/<id>', methods=['GET'])
@limiter.exempt
def get_recipe_for_id(id):
    try:
        recipe = Recipe.query.filter(Recipe.id == id)[0]

        data = {
            "id": recipe.id,
            "title": recipe.title,
            "instructions": recipe.instructions,
            "img": recipe.img,
            "type": recipe.type,
            "time": recipe.time,
            "people": recipe.people,
            "owner": recipe.owner,
            "ingredients": [dict([("id", ingredient.id), ("item", ingredient.item), ("quantity", ingredient.quantity)])
                            for ingredient in recipe.ingredients]
        }
        clear_sessions()
        return return_result(data=data)
    except IndexError:
        clear_sessions()
        return return_result(message="This recipe index does not exist", code=400, status="failure")


@recipes_blueprint.route('/<id>/<approve>', methods=['GET'])
@limiter.exempt
def approve_recipe_for_id(id, approve):
    if approve != config.APPROVE_KEY:
        return return_result(message="Not the right key!", code=400, status="failure")
    try:
        recipe = Recipe.query.filter(Recipe.id == id)[0]

        recipe = Recipe(id=recipe.id, title=recipe.title,
                        instructions=recipe.instructions,
                        img=recipe.img, type=recipe.type, time=recipe.time,
                        people=recipe.people, owner=recipe.owner, approved=True)
        db_session.add(recipe)
        clear_sessions()
        return return_result(data=data)
    except IndexError:
        clear_sessions()
        return return_result(message="This recipe index does not exist", code=400, status="failure")


@recipes_blueprint.route('/add', methods=['POST'])
def add_recipe():
    data = request.data
    recipe_data = json.loads(data.decode("utf-8"))

    recipe = Recipe(title=recipe_data['title'].replace("‘", "'"),
                    instructions=recipe_data['instructions'].replace("‘", "'"),
                    img=recipe_data['img'], type=recipe_data['type'], time=recipe_data['time'].replace("‘", "'"),
                    people=recipe_data['people'], owner=recipe_data['owner'].replace("‘", "'"), approved=False)
    db_session.add(recipe)

    for ingredient in recipe_data['ingredients']:
        ingredient = Ingredient(item=ingredient['item'].replace("‘", "'"),
                                quantity=ingredient['quantity'].replace("‘", "'"))
        db_session.add(ingredient)
        recipe.ingredients.append(ingredient)

    try:
        db_session.commit()
        clear_sessions()
        return return_result(data=recipe_data)
    except Exception:
        db_session.rollback()
        clear_sessions()
        return return_result(
            message="Dit recept kon niet worden toegevoegd aan veganwinners, controleer je velden of probeer het later opnieuw.",
            code=500, status="failure")


@classify_blueprint.route('/food', methods=['POST'])
@limiter.exempt
def is_food_on_img():
    input = request.data
    input_data = json.loads(input.decode("utf-8"))

    try:
        return return_result(data=has_food(input_data['img_url']))
    except Exception:
        return return_result(
            message="Er is een onverwachte fout opgetreden. Neem a.u.b. contact op met veganwinners.",
            code=500, status="failure")


@classify_blueprint.route('/ingredients', methods=['POST'])
@limiter.exempt
def ingredients_on_img():
    input = request.data
    input_data = json.loads(input.decode("utf-8"))

    try:
        forbidden = forbidden_ingredients(input_data['img_url'])
        used = vegi_ingredients_used(input_data['img_url'])
        data = {
            "forbidden": forbidden,
            "used": used
        }
        return return_result(data=data)
    except Exception:
        return return_result(
            message="Er is een onverwachte fout opgetreden. Neem a.u.b. contact op met veganwinners.",
            code=500, status="failure")


@app.errorhandler(500)
def server_error(e):
    return return_result(code=500, status="error", message=str(e))


app.register_blueprint(recipes_blueprint, url_prefix='/api/recipes')
app.register_blueprint(classify_blueprint, url_prefix='/api/classify')
