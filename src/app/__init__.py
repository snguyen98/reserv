from flask import Flask
import yaml
import logging
import logging.config
import os

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    with app.open_instance_resource("config.yaml") as f:
        config = yaml.safe_load(f.read())

    logging.config.dictConfig(config["logging"])
    
    key_path = os.path.join(app.instance_path, config["key_path"])

    if not os.path.isfile(key_path):
        from .tools.generate_key import generate_key
        generate_key(key_path)

    try:
        with open(key_path, "r") as f:
            key = f.read()

    except:
        logging.error("App key invalid or not found")
        return
    
    app.config.from_mapping(
        SECRET_KEY = key,
        DATABASE = os.path.join(app.instance_path, config["db_path"])
    )

    logging.info("Started app")

    from .views.schedule import schedule_bp
    app.register_blueprint(schedule_bp)
    logging.info("Registered schedule view blueprint")

    from .views.auth import auth_bp
    app.register_blueprint(auth_bp)
    logging.info("Registered auth view blueprint")

    from .views.account import account_bp
    app.register_blueprint(account_bp)
    logging.info("Registered account view blueprint")

    from .handlers.schedule_handler import schedule_handler_bp
    app.register_blueprint(schedule_handler_bp)
    logging.info("Registered schedule handler blueprint")

    app.add_url_rule("/", endpoint="index")

    from .data.db import init_app
    init_app(app)
    
    return app

class ConsoleFilter(logging.Filter):
    def filter(self, record):
        filter_strs = [
             "Press CTRL+C to quit",
             "This is a development server. Do not use it in a production deployment. Use a production WSGI server instead."
        ]
        return not any(filter_str in record.getMessage() for filter_str in filter_strs)
    

class WebRequestFilter(logging.Filter):
    def filter(self, record):
        filter_strs = [
             "HTTP/1.1"
        ]
        return not any(filter_str in record.getMessage() for filter_str in filter_strs)