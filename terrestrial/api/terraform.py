import logging
from flask import request
from celery_once import AlreadyQueued

import terrestrial.config as config
from terrestrial.core import terraform


logger = logging.getLogger(f'{__name__}.terraform')


def list_configurations():
    """
    Lists existing configurations
    """
    body = '\n'.join(config.TF_CONFIGURATIONS)
    return body, 200


def execute(config, action):
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

        logger.debug(f'Performing terraform {action} with {delay}s delay')

    var = dict(zip(
        [ k for k in request.form ],
        [ request.form[k] for k in request.form ]))

    logger.debug(
        f'Passing following variables to Terraform: {var}')

    try:
        task = terraform.apply_async((config, action, var), countdown=delay)
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
