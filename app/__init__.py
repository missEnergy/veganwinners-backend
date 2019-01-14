import json

import requests
from cloudinary.uploader import upload
from flask import Blueprint, request
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import or_
from app import config
from app.clarifai import has_food, forbidden_ingredients, vegi_ingredients_used
from app.database import init_db, db_session, clear_sessions
from app.helpers import return_result
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.models.review import Review

application = Flask(__name__)
CORS(application)
limiter = Limiter(
    application,
    key_func=get_remote_address,
    default_limits=["20 per day", "10 per hour"]
)

init_db()

classify_blueprint = Blueprint('classify', __name__)
recipes_blueprint = Blueprint('recipes', __name__)


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
        "likes": recipe.likes,
        "ingredients": [dict([("id", ingredient.id), ("item", ingredient.item), ("quantity", ingredient.quantity)])
                        for ingredient in recipe.ingredients]
    } for recipe in recipes]

    data = sorted(data, key=lambda x: x.get('id'), reverse=True)

    clear_sessions()

    return return_result(data=data)


@recipes_blueprint.route('/reviews', methods=['GET'])
@limiter.exempt
def get_all_recipe_reviews():
    reviews = Review.query

    data = [{
        "id": review.id,
        "recipe_id": review.recipe_id,
        "credit": review.credit,
        "text": review.text,
        "approved": review.approved
    } for review in reviews]

    clear_sessions()

    return return_result(data=data)


@recipes_blueprint.route('/approved/<search>', methods=['GET'])
@limiter.exempt
def get_all_recipes_approved(search):
    if search == '*':
        recipes = Recipe.query.filter(Recipe.approved)
    else:
        recipes = Recipe.query.filter(Recipe.approved).filter(or_(Recipe.title.like("%" + search + "%"),
                                                              Recipe.instructions.like("%" + search + "%")))

    data = [{
        "id": recipe.id,
        "title": recipe.title,
        "instructions": recipe.instructions,
        "img": recipe.img,
        "type": recipe.type,
        "time": recipe.time,
        "people": recipe.people,
        "owner": recipe.owner,
        "likes": recipe.likes,
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
        recipe = Recipe.query.filter(Recipe.id == id, Recipe.approved)[0]

        data = {
            "id": recipe.id,
            "title": recipe.title,
            "instructions": recipe.instructions,
            "img": recipe.img,
            "type": recipe.type,
            "time": recipe.time,
            "people": recipe.people,
            "owner": recipe.owner,
            "likes": recipe.likes,
            "ingredients": [dict([("id", ingredient.id), ("item", ingredient.item), ("quantity", ingredient.quantity)])
                            for ingredient in recipe.ingredients],
            "reviews": [dict([("id", review.id), ("credit", review.credit), ("text", review.text)]) for review in
                        recipe.reviews if review.approved]
        }
        clear_sessions()
        return return_result(data=data)
    except IndexError:
        clear_sessions()
        return return_result(message="This recipe index does not exist", code=400, status="failure")


@recipes_blueprint.route('/<id>/<approve>', methods=['GET'])
@limiter.exempt
def get_recipe_for_id_using_approval(id, approve):
    if approve != config.APPROVE_KEY:
        return return_result(message="Not the right approve key!", code=400, status="failure")
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
            "likes": recipe.likes,
            "ingredients": [dict([("id", ingredient.id), ("item", ingredient.item), ("quantity", ingredient.quantity)])
                            for ingredient in recipe.ingredients]
        }
        clear_sessions()
        return return_result(data=data)
    except IndexError:
        clear_sessions()
        return return_result(message="This recipe index does not exist", code=400, status="failure")


@recipes_blueprint.route('/approve/<id>/<approve>', methods=['GET'])
@limiter.exempt
def approve_recipe_for_id(id, approve):
    if approve != config.APPROVE_KEY:
        return return_result(message="Not the right approve key!", code=400, status="failure")
    try:
        for recipe in Recipe.query.filter(Recipe.id == id):
            recipe.approved = True
        db_session.commit()
        clear_sessions()
        return return_result(data="approved " + id)
    except IndexError:
        clear_sessions()
        return return_result(message="This recipe index does not exist", code=400, status="failure")


@recipes_blueprint.route('/approve/review/<review_id>/<approve>', methods=['GET'])
@limiter.exempt
def approve_review_for_recipe(review_id, approve):
    if approve != config.APPROVE_KEY:
        return return_result(message="Not the right approve key!", code=400, status="failure")
    try:
        for review in Review.query.filter(Review.id == review_id):
            review.approved = True
        db_session.commit()
        clear_sessions()
        return return_result(data="approved review " + review_id)
    except IndexError:
        clear_sessions()
        return return_result(message="This review index does not exist", code=400, status="failure")


@recipes_blueprint.route('/<id>/likes', methods=['GET'])
def add_like_for_recipe_id(id):
    try:
        for recipe in Recipe.query.filter(Recipe.id == id):
            recipe.likes = recipe.likes + 1
        db_session.commit()
        clear_sessions()
        return return_result(data="incremented like for recipe with id: " + id)
    except IndexError:
        clear_sessions()
        return return_result(message="This recipe index does not exist", code=400, status="failure")


@recipes_blueprint.route('/add', methods=['POST'])
@limiter.exempt
def add_recipe():
    data = request.data
    recipe_data = json.loads(data.decode("utf-8"))

    if not recipe_data['img'].startswith("https://res.cloudinary.com/" + config.CLOUD_NAME + "/image/upload/"):
        return return_result(
            message="Je hebt geen geldig plaatje geupload.",
            code=500, status="failure")
    recipe = Recipe(title=recipe_data['title'].replace("‘", "'"),
                    instructions=recipe_data['instructions'].replace("‘", "'"),
                    img=recipe_data['img'], type=recipe_data['type'], time=recipe_data['time'].replace("‘", "'"),
                    people=recipe_data['people'], owner=recipe_data['owner'].replace("‘", "'"), approved=False, likes=0)
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
        return return_result(message="Je bereidingswijze is te lang, kort hem a.u.b. wat in.", code=500, status="failure")


@recipes_blueprint.route('/review', methods=['POST'])
def add_review():
    try:
        data = request.data
        review_data = json.loads(data.decode("utf-8"))
        for recipe in Recipe.query.filter(Recipe.id == review_data['id']):
            review = Review(credit=review_data['credit'].replace("‘", "'"),
                            text=review_data['text'].replace("‘", "'"), approved=False)
            db_session.add(review)
            recipe.reviews.append(review)
        db_session.commit()
        clear_sessions()
        return return_result(data="added review for recipe with id: " + review_data['id'])
    except IndexError:
        clear_sessions()
        return return_result(message="This recipe index does not exist", code=400, status="failure")


@classify_blueprint.route('/upload-image', methods=['POST'])
def upload_image():
    try:
        image = request.files['img']
        upload_result = upload(image, upload_preset=config.UPLOAD_PRESET, api_key=config.API_KEY,
                               api_secret=config.API_SECRET,
                               cloud_name=config.CLOUD_NAME, return_delete_token=True)
        token = upload_result['delete_token']
        img_url = upload_result['secure_url']

        if has_food(img_url):
            forbidden = forbidden_ingredients(img_url)
            used = vegi_ingredients_used(img_url)
            data = {
                "food": True,
                "forbidden": forbidden,
                "used": used,
                "url": img_url
            }
            return return_result(data=data)
        else:
            requests.post("https://api.cloudinary.com/v1_1/" + config.CLOUD_NAME + "/delete_by_token",
                          data={'token': token})
            return return_result(data={'food': False})
    except Exception:
        return return_result(
            message="Er is een onverwachte fout opgetreden. Neem a.u.b. contact op met veganwinners.",
            code=500, status="failure")


application.register_blueprint(recipes_blueprint, url_prefix='/api/recipes')
application.register_blueprint(classify_blueprint, url_prefix='/api/classify')


@application.errorhandler(500)
def server_error(e):
    return return_result(code=500, status="error", message=str(e))
