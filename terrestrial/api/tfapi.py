import sys

from flask import Flask, request
from flask_httpauth import HTTPTokenAuth
from werkzeug.routing import BaseConverter

import terrestrial.config as config
from terrestrial.core.tasks import apply, destroy


auth = HTTPTokenAuth(scheme='Token')
api = Flask('terrestrial')
logger = api.logger


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        self.regex = args[0]

api.url_map.converters['regex'] = RegexConverter


def parse_request_args(bundle_errors=True):
    parser = reqparse.RequestParser(bundle_errors=bundle_errors)
    print(parser.parse_args())

    return dict(parser.parse_args())


@auth.verify_token
def verify_token(token):
    """ 
    Verifies Token from Authorization header
    """
    if config.API_TOKEN is None:
        logger.error(
            'API token is not configured, auth will fail!')
    return token == config.API_TOKEN


@api.route('/api/v1/health')
def health():
    return 'OK', 200


@api.route('/api/v1/configurations', methods=['GET'])
@auth.login_required
def list():
    """
    Lists existing configurations
    """
    body = '\n'.join(config.TF_CONFIGURATIONS)
    return body, 200


@api.route('/api/v1/configurations/<regex("[\w-]+"):config>/<regex("apply|destroy"):action>', methods=['POST'])
@auth.login_required
def handle(config, action):
    """ 
    Performs "terraform <action>" on a given <config>
    """
    async = True if 'async' in request.args else False
    if async:
        logger.debug(f'Performing {action} asynchronously')

    var = dict(zip(
        [ k for k in request.form ], 
        [ request.form[k] for k in request.form ]))

    logger.debug(
        f'Passing following variables to Terraform: {var}')

    try:
        action = globals()[action]
        task = action.s(config=config, var=var).delay()
    except Exception as e:
        body = f'Terraform {action} failed for "{config}": {e}'
        logger.error(body)
        return body, 500

    if async:
        return task.id, 200

    logger.debug(f'Waiting for task {task.id} to finish')
    rc, stdout, stderr = task.wait()
    if rc != 0:
        logger.error(stderr)
        return stderr, 500
    
    return stdout, 200
