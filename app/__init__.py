from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo


# See PEP396.
__version__ = '2.0'

def create_app():
    """
    Construct the core application.
    """
    # Create flask app with CORS enabled.
    app = Flask(__name__)
    app.config['MONGO_URI'] = "mongodb://beacon:admin123@ds046377.mlab.com:46377/beacon?retryWrites=false"
    app.url_map.strict_slashes = False
    CORS(app)
    PyMongo(app)

    # Set app config from settings.
    app.config.from_pyfile('config/settings.py');
    # app.config["MONGO_URI"] = 

    with app.app_context():
        # Import routes.
        from . import routes

        # Register api endpoints.
        app.register_blueprint(routes.api_v1)
        app.register_blueprint(routes.api_v2)

        # Return created app.
        return app
