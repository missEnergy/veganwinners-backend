from app.helpers import return_result
from flask import Blueprint, request
import requests
from app.clarifai import has_food, forbidden_ingredients, vegi_ingredients_used
from cloudinary.uploader import upload
from app import config

classify_blueprint = Blueprint('classify', __name__)


@classify_blueprint.route('/upload-image', methods=['POST'])
def upload_image():
    try:
        image = request.files['img']
        upload_result = upload(image, api_key=config.API_KEY, api_secret=config.API_SECRET,
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
