from .home import home_bp
from .weather import weather_bp
from .tube import tube_bp
from .doc_who import doc_who_bp
from .rowing import rowing_bp
from .auth import auth_bp

def register_blueprints(app):
    app.register_blueprint(home_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(tube_bp)
    app.register_blueprint(doc_who_bp)
    app.register_blueprint(rowing_bp)
    app.register_blueprint(auth_bp)
