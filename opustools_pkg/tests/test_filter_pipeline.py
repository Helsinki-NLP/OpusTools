import unittest
from yaml import load, Loader

from opustools_pkg.filter.pipeline import FilterPipeline

class TestFilterPipeline(unittest.TestCase):

    def test_from_config(self):
        with open('filter.yml') as config_file:
            config = load(config_file, Loader=Loader)

        fp = FilterPipeline.from_config(config)

        self.assertEqual(len(fp.filters), 5)

