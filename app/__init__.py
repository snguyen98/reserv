from flask import Flask

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '90a9eee2f650fa61390458ae4b717e14503f7cbe26fabca850b67db78c73319b'
    
    from .views.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from .views.main import main_bp
    app.register_blueprint(main_bp)

    from .handlers.schedule_handler import schedule_bp
    app.register_blueprint(schedule_bp)

    app.add_url_rule("/", endpoint="index")
    
    return app
