from flask import Flask

from config import Config
from routes.web import web_blueprint
from routes.api import api_blueprint


def create_app() -> Flask:
    try:
        app = Flask(__name__, template_folder="templates", static_folder="static")
        app.config.from_object(Config)
        app.register_blueprint(web_blueprint)
        app.register_blueprint(api_blueprint, url_prefix="/api")
    except Exception as e:
        print(f"Error creating Flask app: {e}")
        raise e
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5001, debug=Config.DEBUG)
