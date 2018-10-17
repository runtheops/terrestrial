import os
import logging
from pathlib import Path

from celery_once import QueueOnce
from celery.signals import worker_ready
from celery.utils.log import get_logger, get_task_logger

from terrestrial.errors import TerrestrialRetryError
from .celery import app
from .tfconfig import TerraformConfig
from .tfworker import TerraformWorker


logger = get_logger(__name__)
task_logger = get_task_logger(__name__)


@worker_ready.connect
def init(*args, **kwargs):
    """
    Initializes all Terraform configurations 
    found under configurations path
    """

    logger.debug(f'Starting configurations initialization')

    for p in Path(app.conf.TF_CONF_PATH).iterdir():
        if p.is_dir():
            logger.debug(f'Initializing {p.stem}')

            with TerraformConfig(path=p.absolute(), logger=logger) as c:
                rc_i, stdout, stderr = c.init()
                if rc_i != 0:
                    logger.error(
                        f'Initialization failed for "{p.stem}"')

                rc_v, stdout, stderr = c.validate()
                if rc_v != 0:
                    logger.error(
                        f'Configuration "{p.stem}" is invalid')

                if rc_i != 0 or rc_v != 0:
                    logger.error('Shutting down!')
                    os.kill(os.getpid(), 15)

    logger.info('Initialized. Ready to process tasks')


@app.task(bind=True)
def apply(self, config, var={}):
    """
    Performs 'terraform apply' on a configuration
    given corresponding variables as <var>
    """

    task_logger.debug('Spawning Terraform apply process for {config}')
    with TerraformWorker(
        config_path=f'{app.conf.TF_CONF_PATH}/{config}', 
        workspace='default', logger=task_logger) as w:

        try:
            rc, stdout, stderr = w.apply(var=var)
            return rc, stdout, stderr
        except TerrestrialRetryError as exc:
            raise self.retry(exc=exc, countdown=5)


@app.task(bind=True)
def destroy(self, config, var={}):
    """
    Performs "terraform destroy" on a configuration
    given corresponding variables as <var>
    """

    task_logger.debug('Spawning Terraform destroy process for {config}')
    with TerraformWorker(
        config_path=f'{app.conf.TF_CONF_PATH}/{config}', 
        workspace='default', logger=task_logger) as w:

        try:
            rc, stdout, stderr = w.destroy(var=var)
            return rc, stdout, stderr
        except TerrestrialRetryError as exc:
            raise self.retry(exc=exc, countdown=5)
