from flask import Blueprint
from app.models.recipe import Recipe
from app.helpers import return_result

recipes_blueprint = Blueprint('recipes', __name__)


@recipes_blueprint.route('/<limit>')
def get_all_recipes(limit):
    recipes = Recipe.query \
        .limit(limit)

    data = [{
        "id": recipe.id,
        "title": recipe.title,
        "directions": recipe.directions
    } for recipe in recipes]

    return return_result(data=data)
