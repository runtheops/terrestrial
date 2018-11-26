import unittest
from shutil import rmtree
from pathlib import Path

from terrestrial.core.tfworker import TerraformWorker

from .helpers import ignore_warnings


class TestTerraformActions(unittest.TestCase):
    '''
    Attempts validation on broken Terraform configuration
    '''
    @classmethod
    @ignore_warnings
    def setUpClass(self):
        self.tests_path = Path(__file__).parents[0]
        self.worker = TerraformWorker(
            config_path=f'{self.tests_path}/configurations/valid',
            workspace='default')


    @classmethod
    def tearDownClass(self):
        try:
            rmtree(f'{self.worker._config.path}/.terraform')
        except FileNotFoundError:
            pass

        self.worker._config.close()


    @ignore_warnings
    def test_apply(self):
        rc, stdout, stderr = self.worker.apply()
        self.assertNotEqual(rc, 0, f'non-zero exit code on apply: {stderr}')


    @ignore_warnings
    def test_destroy(self):
        rc, stdout, stderr = self.worker.destroy()
        self.assertNotEqual(rc, 0, f'non-zero exit code on destroy: {stderr}')
