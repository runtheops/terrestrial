import re
import logging

from python_terraform import Terraform, IsFlagged

from terrestrial.errors import TerrestrialFatalError
from .tfconfig import TerraformConfig


KWARGS_MAPPING = {
    'plan': {
        'input': False
    },
    'apply': {
        'input': False,
        'auto_approve': True
    },
    'destroy': {
        'input': False,
        'auto_approve': True
    }
}


class TerraformWorker:
    def __init__(self, config_path, workspace, isolate=True, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.isolate = isolate
        self.config_path = config_path
        self.tf = Terraform(working_dir=self.config_path)
        self.workspace = workspace

    def __getattr__(self, item):
        def wrapper(*args, **kwargs):
            kwargs.update({'no_color': IsFlagged})

            if item in KWARGS_MAPPING:
                kwargs.update(KWARGS_MAPPING[item])

            rc, stdout, stderr = self.tf.cmd(
                item, *args, **kwargs)

            return rc, stdout.strip(), stderr.strip()

        return wrapper

    @property
    def config_path(self):
        return self._config_path

    @config_path.setter
    def config_path(self, c):
        self._config = TerraformConfig(c)
        if self.isolate:
            self._config_path = self._config.clone()
        else:
            self._config_path = self._config.path

    @property
    def workspace(self):
        return self._workspace

    @workspace.setter
    def workspace(self, w):    
        expr = re.compile('^[a-z0-9\-_.~]{1,255}$', re.IGNORECASE)

        if not re.match(expr, w):
            raise TerrestrialFatalError(
                'Workspace name must contain only URL safe characters.')    

        rc, stdout, stderr = self.tf.cmd(
            'workspace', 'new', w, '-no-color')

        if rc != 0:
            if 'already exists' in stderr:
                rc, stdout, stderr = self.tf.cmd(
                    'workspace', 'select', w ,'-no-color')

                if rc != 0:
                    raise TerrestrialFatalError(
                        f'Failed to set workspace to {self.workspace}')

        self.logger.debug(
            f'Switched workspace to {self.workspace}')

        self._workspace = w

    def __enter__(self):
        return self

    def __exit__(self, exc_t, exc_v, traceback):
        self._config.close()
