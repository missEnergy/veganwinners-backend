from flask import jsonify
from functools import wraps
from flask import redirect, request, current_app


def return_result(status="success", code=200, message="", data=None):
    return jsonify(status=status, code=code, message=message, data=data)
