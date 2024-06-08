from flask import Flask

def create_app():
    import logging.config
    logging.basicConfig(
        filename='app/logs/app.log',
        encoding='utf-8',
        format='%(asctime)8s     %(levelname)8s     %(message)8s',
        level=logging.DEBUG
    )
    
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '90a9eee2f650fa61390458ae4b717e14503f7cbe26fabca850b67db78c73319b'
    
    from .views.main import main_bp
    app.register_blueprint(main_bp)

    from .views.auth import auth_bp
    app.register_blueprint(auth_bp)

    from .views.account import account_bp
    app.register_blueprint(account_bp)

    from .handlers.schedule_handler import schedule_bp
    app.register_blueprint(schedule_bp)

    app.add_url_rule("/", endpoint="index")
    
    return app
