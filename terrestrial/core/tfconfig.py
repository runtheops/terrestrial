import logging
from pathlib import Path
from tempfile import mkdtemp
from shutil import copytree, rmtree

from python_terraform import Terraform, IsFlagged

from terrestrial.errors import TerrestrialFatalError


class TerraformConfig:
    def __init__(self, path, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.path = path
        self.name = Path(path).stem

        self._clone_path = None
 
    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, p):
        if not (Path(p).is_dir() and Path(p).is_absolute()):
            raise TerrestrialFatalError(
                'Configuration path must be an absolute path to a directory')

        self._path = p

    def clone(self):
        if not self._clone_path:
            self._clone_path = copytree(
                self.path, f'{mkdtemp()}/{self.name}')

        return self._clone_path

    def close(self):
        if self._clone_path and Path(self._clone_path).exists():
            rmtree(Path(self._clone_path).parent)

    def _tfcmd(self, cmd, **kwargs):
        tf = Terraform(working_dir=self.path)
        return tf.cmd(cmd, no_color=IsFlagged, **kwargs)

    def init(self):
        return self._tfcmd('init')

    def validate(self):
        return self._tfcmd('validate', check_variables=False)

    def __enter__(self):
        return self

    def __exit__(self, exc_t, exc_v, traceback):
        self.close()

    def __del__(self):
        self.close()
