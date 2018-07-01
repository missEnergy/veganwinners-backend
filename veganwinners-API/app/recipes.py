from flask import Blueprint, request
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.helpers import return_result
from app.database import db_session, clear_sessions
import json

recipes_blueprint = Blueprint('recipes', __name__)


@recipes_blueprint.route('/<limit>', methods=['GET'])
def get_all_recipes(limit):
    recipes = Recipe.query \
        .limit(limit)

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


@recipes_blueprint.route('/one/<id>', methods=['GET'])
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
            "ingredients": [dict([("id", ingredient.id), ("item", ingredient.item), ("quantity", ingredient.quantity)]) for ingredient in recipe.ingredients]
        }
        clear_sessions()
        return return_result(data=data)
    except IndexError:
        clear_sessions()
        return return_result(message="This recipe index does not exist", code=400, status="failure")


@recipes_blueprint.route('/add', methods=['POST'])
def add_recipe():
    data = request.data
    recipe_data = json.loads(data.decode("utf-8"))

    recipe = Recipe(title=recipe_data['title'], instructions=recipe_data['instructions'],
                    img=recipe_data['img'], type=recipe_data['type'], time=recipe_data['time'],
                    people=recipe_data['people'], owner=recipe_data['owner'])
    db_session.add(recipe)

    for ingredient in recipe_data['ingredients']:
        ingredient = Ingredient(item=ingredient['item'], quantity=ingredient['quantity'])
        db_session.add(ingredient)
        recipe.ingredients.append(ingredient)

    try:
        db_session.commit()
        clear_sessions()
        return return_result(data=recipe_data)
    except Exception:
        db_session.rollback()
        clear_sessions()
        return return_result(message="Dit ingredient kon niet worden toegevoegd aan veganwinners, controleer je velden of probeer het later opnieuw.", code=500, status="failure")