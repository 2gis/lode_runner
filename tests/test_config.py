import unittest
import os

from lode_runner.config import load_json


class ConfigTest(unittest.TestCase):
    def test_config_returned(self):
        original_config = {
            "key": {
                "subkey": "value"
            },
            "key2": "value2"
        }

        tests_dir = os.path.dirname(os.path.realpath(__file__))
        config = load_json(tests_dir + '/data/config.json', encoding='utf-8')
        self.assertEqual(original_config, config)