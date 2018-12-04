from app.helpers import return_result
from flask import Blueprint, request
import json
from app.clarifai import has_food, forbidden_ingredients, vegi_ingredients_used

classify_blueprint = Blueprint('classify', __name__)


@classify_blueprint.route('/food', methods=['POST'])
# @limiter.exempt
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
# @limiter.exempt
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

