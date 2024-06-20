from flask import Flask
import yaml
import logging

def create_app():
    import logging.config
    
    with open("app/log_config.yaml", "rt") as f:
        log_config = yaml.safe_load(f.read())

    logging.config.dictConfig(log_config)

    logging.info("Starting app...")
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '90a9eee2f650fa61390458ae4b717e14503f7cbe26fabca850b67db78c73319b'
    
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