import unittest
from os import listdir
from shutil import rmtree
from pathlib import Path

from terrestrial.core.tfconfig import TerraformConfig

from .helpers import ignore_warnings


class TestValidTerraformConfig(unittest.TestCase):
    '''
    Tests TerraformConfig base functionality
    using minimal valid configuration
    '''
    @classmethod
    def setUpClass(self):
        self.tests_path = Path(__file__).parents[0]
        self.config = TerraformConfig(
            path=f'{self.tests_path}/configurations/valid')


    @classmethod
    def tearDownClass(self):
        try:
            rmtree(f'{self.config.path}/.terraform')
        except FileNotFoundError:
            pass

        self.config.close()


    @ignore_warnings
    def test_config_init(self):
        rc, stdout, stderr = self.config.init()
        self.assertEqual(rc, 0, f'non-zero exit code on init: {stderr}')


    @ignore_warnings
    def test_config_is_valid(self):
        rc, stdout, stderr = self.config.validate()
        self.assertEqual(rc, 0, f'terraform config is invalid: {stderr}')


    def test_config_clone(self):
        clone = self.config.clone()
        config_content = listdir(self.config.path)
        clone_content = listdir(clone)
        self.assertEqual(config_content, clone_content)


class TestValidUnsetTerraformConfig(unittest.TestCase):
    '''
    Tests TerraformConfig base functionality using minimal
    valid configuration with one or more variables not defaulted
    '''
    @classmethod
    def setUpClass(self):
        self.tests_path = Path(__file__).parents[0]
        self.config = TerraformConfig(
            path=f'{self.tests_path}/configurations/valid-unset')


    @classmethod
    def tearDownClass(self):
        try:
            rmtree(f'{self.config.path}/.terraform')
        except FileNotFoundError:
            pass

        self.config.close()


    @ignore_warnings
    def test_config_init(self):
        rc, stdout, stderr = self.config.init()
        self.assertEqual(rc, 0, f'non-zero exit code on init: {stderr}')


    @ignore_warnings
    def test_config_is_valid(self):
        rc, stdout, stderr = self.config.validate()
        self.assertEqual(rc, 0, f'terraform config is invalid: {stderr}')


class TestInvalidTerraformConfig(unittest.TestCase):
    '''
    Attempts validation on broken Terraform configuration
    '''
    @classmethod
    def setUpClass(self):
        self.tests_path = Path(__file__).parents[0]
        self.config = TerraformConfig(
            path=f'{self.tests_path}/configurations/invalid')


    @classmethod
    def tearDownClass(self):
        try:
            rmtree(f'{self.config.path}/.terraform')
        except FileNotFoundError:
            pass

        self.config.close()


    @ignore_warnings
    def test_config_init(self):
        rc, stdout, stderr = self.config.init()
        self.assertNotEqual(rc, 0, f'non-zero exit code on init: {stderr}')


    @ignore_warnings
    def test_config_is_invalid(self):
        rc, stdout, stderr = self.config.validate()
        self.assertNotEqual(rc, 0, 
            f'invalid config passed validation: {stderr}')
