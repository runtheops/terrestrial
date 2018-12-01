import logging
from flask import request

from terrestrial.core import list_celery_tasks, get_task_state, get_task_result


logger = logging.getLogger(f'{__name__}.celery')


def list_tasks(status=None):
    """
    List all tasks filtered by status
    """

    state = None
    if 'state' in request.args:
        state = request.args['state'].upper()

    logger.debug('Listing tasks')
    try:
        task = list_celery_tasks.apply((state,))
        status = task.get()
    except Exception as e:
        body = f'Failed to list tasks: {e}'
        logger.error(body)
        return body, 500

    return status, 200


def get_state(task_id):
    """
    Retrieve status of a task by its ID
    """

    logger.debug(f'Retrieving state of a task {task_id}')
    try:
        task = get_task_state.apply((task_id,))
        status = task.get()
    except Exception as e:
        body = f'Failed to get state of a task "{task_id}": {e}'
        logger.error(body)
        return body, 500

    return status, 200


def get_result(task_id):
    """
    Retrieve result of a task by its ID
    """

    logger.debug(f'Retrieving result of task {task_id}')
    try:
        task = get_task_result.apply((task_id,))
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
