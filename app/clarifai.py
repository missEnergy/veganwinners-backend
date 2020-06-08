from clarifai.rest import ClarifaiApp

from app import config
from app import classify_utils

app = ClarifaiApp(api_key=config.CLARIFAI_KEY)
general_model = app.models.get(classify_utils.general_model)
ingredients_model = app.models.get(classify_utils.ingredients_model)
forbidden = classify_utils.forbidden
translate_ingredient_dict = classify_utils.translate_ingredient_dict


def has_food(img_url):
    classification = general_model.predict_by_url(img_url, min_value=0.90).get('outputs')[0].get("data").get("concepts")
    food_list = [x for x in classification if x.get("name") == 'food']
    if len(food_list) > 0:
        return True
    return False


def forbidden_ingredients(img_url):
    classification = ingredients_model.predict_by_url(img_url, min_value=0.90, max_concepts=5).get('outputs')[0].get(
        "data").get("concepts")
    if classification == None:
        return []
    used_ingredients_list = [x.get('name') for x in classification]
    if used_ingredients_list == None:
        return []
    forbidden_ingredients_list = []
    for x in used_ingredients_list:
        if x in forbidden:
            forbidden_ingredients_list.append(forbidden.get(x))
    return forbidden_ingredients_list


def vegi_ingredients_used(img_url):
    classification = ingredients_model.predict_by_url(img_url, min_value=0.50, max_concepts=15).get('outputs')[0].get(
        "data").get("concepts")
    if classification == None:
        return []
    used_ingredients_list = [x.get('name') for x in classification]
    if used_ingredients_list == None:
        return []
    suggested_ingredients = []
    for x in used_ingredients_list:
        if x in translate_ingredient_dict.keys():
            suggested_ingredients.append(translate_ingredient_dict.get(x))
    return suggested_ingredients
