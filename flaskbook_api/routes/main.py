from flask import Blueprint, jsonify, request

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return jsonify({
        "message": "API 서버 실행됨"
    })

@bp.route("/test", methods=["POST"])
def test():
    data = request.get_json()

    return jsonify({
        "받은값": data
    })