from flask import Flask

from app.extensions import db, migrate, login_manager, csrf
from app.routes import main


def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    app.register_blueprint(main)

    return app