from flask import Blueprint, request
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.helpers import return_result
from app.database import db_session
import json

recipes_blueprint = Blueprint('recipes', __name__)


@recipes_blueprint.route('/<limit>')
def get_all_recipes(limit):
    recipes = Recipe.query \
        .limit(limit)

    data = [{
        "id": recipe.id,
        "title": recipe.title,
        "instructions": recipe.instructions,
        "img": recipe.img,
        "ingredients": [dict([("id", ingredient.id), ("item", ingredient.item), ("quantity", ingredient.quantity)])
                        for ingredient in recipe.ingredients]
    } for recipe in recipes]

    return return_result(data=data)


@recipes_blueprint.route('/one/<id>')
def get_recipe_for_id(id):
    recipe = Recipe.query \
        .filter(Recipe.id == id) \
        .limit(1)[0]

    data = {
        "id": recipe.id,
        "title": recipe.title,
        "instructions": recipe.instructions,
        "img": recipe.img,
        "ingredients": [dict([("id", ingredient.id), ("item", ingredient.item), ("quantity", ingredient.quantity)])
                        for ingredient in recipe.ingredients]
    }

    return return_result(data=data)


# http://www.lizsander.com/programming/2015/09/08/SQLalchemy-part-2.html
@recipes_blueprint.route('/test')
def test_add_recipe():

    recipe = Recipe(title="Een lekker recept", instructions="Zo moet je het maken. Easy!", img="/img/vegan-pasta.jpg")
    ingredient = Ingredient(item='Bier', quantity='10 Liter')
    db_session.add(ingredient)

    recipe.ingredients.append(ingredient)
    db_session.add(recipe)
    db_session.commit()

    return return_result(data="gelukt!!")


@recipes_blueprint.route('/add', methods=['POST'])
def add_recipe():
    # For Headers: Content-Type = application/json, raw Json body:
    data = request.data
    recipe_data = json.loads(data)

    recipe = Recipe(title=recipe_data['title'], instructions=recipe_data['instructions'], img="/img/vegan-pasta.jpg")
    db_session.add(recipe)

    for ingredient in recipe_data['ingredients']:
        ingredient = Ingredient(item=ingredient['item'], quantity=ingredient['quantity'])
        db_session.add(ingredient)
        recipe.ingredients.append(ingredient)

    db_session.commit()

    return return_result(data=recipe_data)
