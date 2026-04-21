from flask import Flask

def create_app():
    app = Flask(__name__)

    # 라우트 등록
    from flaskbook_api.routes import main
    app.register_blueprint(main.bp)

    return app