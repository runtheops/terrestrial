from flask import Blueprint
from flask_httpauth import HTTPTokenAuth

from terrestrial.api import common, terraform, celery

from .converters import add_url_converter, RegexConverter


Blueprint.add_url_converter = add_url_converter

blueprint = Blueprint('api_v1', __name__)
blueprint.add_url_converter('regex', RegexConverter)

auth = HTTPTokenAuth(scheme='Token')


@auth.verify_token
def verify_token(token):
    return common.verify_token(token)


@blueprint.route('/health')
def health():
    return common.health()


@blueprint.route('/configurations', methods=['GET'])
@auth.login_required
def list_configurations():
    return terraform.list_configurations()


@blueprint.route('/configurations/<regex("[\w-]+"):config>/<regex("plan|apply|destroy"):action>', methods=['POST'])
@auth.login_required
def execute(config, action):
    return terraform.execute(config,action)


@blueprint.route('/tasks', methods=['GET'])
@auth.login_required
def list_tasks(status=None):
    return celery.list_tasks(status)


@blueprint.route('/tasks/<regex("[\w-]+"):task_id>', methods=['GET'])
@auth.login_required
def get_task_state(task_id):
    return celery.get_task_state(task_id)


@blueprint.route('/tasks/<regex("[\w-]+"):task_id>/result', methods=['GET'])
@auth.login_required
def get_task_result(task_id):
    return celery.get_task_result(task_id)
