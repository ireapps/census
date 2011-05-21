"""
Not sure what to test in the api yet...
"""

from django.utils import unittest
from django.test.client import Client
from django.test.simple import DjangoTestSuiteRunner
import simplejson
import logging

class TestRunner(DjangoTestSuiteRunner):
    def setup_databases(self,**kwargs):
        pass

    def teardown_databases(self,old_config, **kwargs):
        pass

class ViewTest(unittest.TestCase):
    log = logging.getLogger('ViewTests')
    def test_json_api(self):
        self.log.debug('test_json_api')
        geoids = '10,10001,10001040100'
        geoids = geoids.split(',')
        test = []
        c = Client()
        while geoids:
            test.append(geoids.pop())
            path = "/data/%s.json" % ",".join(test)
            self.log.debug("asking for %s" % path)
            r = c.get(path)
            json_response = simplejson.loads(r.content)
            self.assertEqual(len(test),len(json_response))
            print '.',

    def test_html_api(self):
        self.log.debug('test_html_api')
        geoids = '10,10001,10001040100'
        geoids = geoids.split(',')
        test = []
        c = Client()
        while geoids:
            test.append(geoids.pop())
            path = "/data/%s.html" % ",".join(test)
            self.log.debug("asking for %s" % path)
            r = c.get(path)
            print '.',
