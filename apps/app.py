from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

from apps import db
from apps.config import config


csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = "auth.signup"
login_manager.login_message = ""


def create_app(config_key):
    app = Flask(__name__)
    app.config.from_object(config[config_key])

    db.init_app(app)
    csrf.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)

    # 블루프린트 import는 create_app 안에서 처리
    from apps.crud import views as crud_views
    app.register_blueprint(crud_views.crud, url_prefix="/crud")

    from apps.auth import views as auth_views
    app.register_blueprint(auth_views.auth, url_prefix="/auth")

    from apps.detector import views as dt_views
    app.register_blueprint(dt_views.dt)

        # 커스텀 오류 화면을 등록한다
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)

    return app

def page_not_found(e):
    """404 Not Found"""
    return render_template("404.html"), 404


def internal_server_error(e):
    """500 Internal Server Error"""
    return render_template("500.html"), 500