from flask import Blueprint
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.helpers import return_result
from app.database import db_session

recipes_blueprint = Blueprint('recipes', __name__)


@recipes_blueprint.route('/<limit>')
def get_all_recipes(limit):
    recipes = Recipe.query \
        .limit(limit)

    data = [{
        "id": recipe.id,
        "title": recipe.title,
        "instructions": recipe.instructions,
        "ingredients": recipe.ingredients
    } for recipe in recipes]

    return return_result(data=data)


@recipes_blueprint.route('/test')
def add_recipe():

    recipe = Recipe(title="Een lekker recept", instructions="Zo moet je het maken. Easy!")
    ingredient = Ingredient(item='Bier', quantity='10 Liter')
    db_session.add(ingredient)

    recipe.ingredients.append(ingredient)
    db_session.add(recipe)
    db_session.flush()

    # http://www.lizsander.com/programming/2015/09/08/SQLalchemy-part-2.html

    return return_result(data="gelukt!!")
