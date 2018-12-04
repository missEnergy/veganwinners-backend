from flask import jsonify


def return_result(status="success", code=200, message="", data=None):
    return jsonify(status=status, code=code, message=message, data=data)
