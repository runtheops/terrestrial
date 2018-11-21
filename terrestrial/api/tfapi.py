import sys

from flask import Flask, request
from flask_httpauth import HTTPTokenAuth
from celery_once import AlreadyQueued
from werkzeug.routing import BaseConverter

import terrestrial.config as config
from terrestrial.core import *


auth = HTTPTokenAuth(scheme='Token')
api = Flask('terrestrial')
logger = api.logger


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        self.regex = args[0]

api.url_map.converters['regex'] = RegexConverter


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
def list_configurations():
    """
    Lists existing configurations
    """
    body = '\n'.join(config.TF_CONFIGURATIONS)
    return body, 200


@api.route('/api/v1/configurations/<regex("[\w-]+"):config>/<regex("apply|destroy"):action>', methods=['POST'])
@auth.login_required
def perform_tf_action(config, action):
    """
    Performs "terraform <action>" on a given <config>
    """
    async = True if 'async' in request.args else False
    if async:
        logger.debug(f'Performing {action} asynchronously')

    delay = 0
    if 'delay' in request.args:
        try:
            delay = int(request.args['delay'])
        except ValueError:
            body = f'Execution delay must be an integer'
            return body, 500

        logger.debug(f'Performing {action} with {delay}s delay')

    var = dict(zip(
        [ k for k in request.form ], 
        [ request.form[k] for k in request.form ]))

    logger.debug(
        f'Passing following variables to Terraform: {var}')

    try:
        action = globals()[action]
        task = action.apply_async((config, var), countdown=delay)
    except AlreadyQueued as e:
        body = f'This task is already queued! Cooldown time left: {e}s'
        logger.error(body)
        return body, 500
    except Exception as e:
        body = f'Terraform task failed for "{config}": {e}'
        logger.error(body)
        return body, 500

    if async:
        return task.id, 201

    logger.debug(f'Waiting for task {task.id} to finish')
    rc, stdout, stderr = task.wait()
    if rc != 0:
        logger.error(stderr)
        return stderr, 500

    return stdout, 201


@api.route('/api/v1/tasks', methods=['GET'])
@auth.login_required
def list_celery_tasks(status=None):
    """
    List all tasks filtered by status
    """

    state = None
    if 'state' in request.args:
        state = request.args['state'].upper()

    logger.debug('Listing tasks')
    try:
        task = list_tasks.apply((state,))
        status = task.get()
    except Exception as e:
        body = f'Failed to list tasks: {e}'
        logger.error(body)
        return body, 500

    return status, 200


@api.route('/api/v1/tasks/<regex("[\w-]+"):task_id>', methods=['GET'])
@auth.login_required
def get_task_state(task_id):
    """
    Retrieve status of a task by its ID
    """

    logger.debug(f'Retrieving state of a task {task_id}')
    try:
        task = get_state.apply((task_id,))
        status = task.get()
    except Exception as e:
        body = f'Failed to get state of a task "{task_id}": {e}'
        logger.error(body)
        return body, 500

    return status, 200


@api.route('/api/v1/tasks/<regex("[\w-]+"):task_id>/result', methods=['GET'])
@auth.login_required
def get_task_result(task_id):
    """
    Retrieve result of a task by its ID
    """

    logger.debug(f'Retrieving result of task {task_id}')
    try:
        task = get_result.apply((task_id,))
        if task.get():
            rc, stdout, stderr = task.get()
        else:
            raise RuntimeError(f'ID is incorrect or task is still pending')
    except Exception as e:
        body = f'Failed to get results of a task "{task_id}": {e}'
        logger.error(body)
        return body, 500

    if rc != 0:
        return stderr, 500

    return stdout, 200
