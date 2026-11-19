
from flask import Flask

from app.extensions import db, migrate, login_manager, csrf
from app.routes.main import main
from app.routes.auth import auth
from app.routes.projects import projects
from app.models import User
from app.routes.requirements import requirements
from app.models.test_suite import TestSuite
from app.routes.test_suites import test_suites
from app.routes.test_cases import test_cases
from app.routes.test_runs import test_runs


def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(projects)
    app.register_blueprint(requirements)
    app.register_blueprint(test_suites)
    app.register_blueprint(test_cases)
    app.register_blueprint(test_runs)

    return app
