import json
from app.helpers import return_result
from flask import Blueprint, request
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.models.review import Review
from app.database import db_session, clear_sessions
from app import config

recipes_blueprint = Blueprint('recipes', __name__)


@recipes_blueprint.route('/', methods=['GET'])
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


@recipes_blueprint.route('/approved', methods=['GET'])
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
        "likes": recipe.likes,
        "ingredients": [dict([("id", ingredient.id), ("item", ingredient.item), ("quantity", ingredient.quantity)])
                        for ingredient in recipe.ingredients]
    } for recipe in recipes]

    data = sorted(data, key=lambda x: x.get('id'), reverse=True)

    clear_sessions()

    return return_result(data=data)


@recipes_blueprint.route('/<id>', methods=['GET'])
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


@recipes_blueprint.route('/<id>/<review_id>/<approve>', methods=['GET'])
def get_review_for_recipe_using_approval(id, review_id, approve):
    if approve != config.APPROVE_KEY:
        return return_result(message="Not the right approve key!", code=400, status="failure")
    try:
        recipe = Recipe.query.filter(Recipe.id == id)[0]

        data = {
            "review": [dict([("id", review.id), ("credit", review.credit), ("text", review.text)]) for review in
                       recipe.reviews if review.id == review_id][0],
            "recipe_title": recipe.title
        }
        clear_sessions()
        return return_result(data=data)
    except IndexError:
        clear_sessions()
        return return_result(message="This recipe index does not exist", code=400, status="failure")


@recipes_blueprint.route('/approve/review/<review_id>/<approve>', methods=['GET'])
def approve_review_for_recipe(review_id, approve):
    if approve != config.APPROVE_KEY:
        return return_result(message="Not the right approve key!", code=400, status="failure")
    try:
        for review in Review.query.filter(Review.id == review_id):
            review.approved = True
        db_session.commit()
        clear_sessions()
        return return_result(data="approved review" + review_id)
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
def add_recipe():
    data = request.data
    recipe_data = json.loads(data.decode("utf-8"))

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
        return return_result(
            message="Dit recept kon niet worden toegevoegd aan veganwinners, "
                    "controleer je velden of probeer het later opnieuw.",
            code=500, status="failure")


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
