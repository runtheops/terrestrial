from flask import Flask

from .v1 import blueprint as api_v1


api = Flask('terrestrial')
api.register_blueprint(api_v1, url_prefix='/api/v1')
