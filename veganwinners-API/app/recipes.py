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
        "ingredients": [dict([("id", ingredient.id), ("item", ingredient.item), ("quantity", ingredient.quantity)])
                        for ingredient in recipe.ingredients]
    } for recipe in recipes]

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
            "ingredients": [dict([("id", ingredient.id), ("item", ingredient.item), ("quantity", ingredient.quantity)]) for ingredient in recipe.ingredients]
        }

        clear_sessions()

        return return_result(data=data)
    except IndexError:
        return return_result(message="This recipe index does not exist", code=400, status="failure")


# # http://www.lizsander.com/programming/2015/09/08/SQLalchemy-part-2.html
# @recipes_blueprint.route('/test')
# def test_add_recipe():
#
#     recipe = Recipe(title="Een lekker recept", instructions="Zo moet je het maken. Easy!", img="/img/vegan-pasta.jpg")
#     ingredient = Ingredient(item='Bier', quantity='10 Liter')
#     db_session.add(ingredient)
#
#     recipe.ingredients.append(ingredient)
#     db_session.add(recipe)
#
#     try:
#       db_session.commit()
#     except Exception, e:
#       db_session.rollback()
#
#     return return_result(data="gelukt!!")

@recipes_blueprint.route('/add', methods=['POST'])
def add_recipe():
    # For Headers: Content-Type = application/json, raw Json body:
    data = request.data
    recipe_data = json.loads(data)

    recipe = Recipe(title=recipe_data['title'], instructions=recipe_data['instructions'],
                    img=recipe_data['img'], type=recipe_data['type'], time=recipe_data['time'],
                    people=recipe_data['people'])
    db_session.add(recipe)

    for ingredient in recipe_data['ingredients']:
        ingredient = Ingredient(item=ingredient['item'], quantity=ingredient['quantity'])
        db_session.add(ingredient)
        recipe.ingredients.append(ingredient)

    try:
        db_session.commit()
    except Exception:
        db_session.rollback()

    clear_sessions()

    return return_result(data=recipe_data)
