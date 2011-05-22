from django.utils import unittest
from django.test.client import Client
from django.test.simple import DjangoTestSuiteRunner
from django.core.urlresolvers import get_resolver, Resolver404
import simplejson
import logging
import mongoutils


class TestRunner(DjangoTestSuiteRunner):
    def setup_databases(self,**kwargs):
        pass

    def teardown_databases(self,old_config, **kwargs):
        pass

class DataTest(unittest.TestCase):
    # Stub. More mongoutils tests here.
    log = logging.getLogger('DataTests')
    def test_mongo_delaware(self):
        self.log.debug('test_mongo_delaware')
        g = mongoutils.get_geography("10")
        self.assertEqual(g['geoid'], "10")
        self.assertEqual(g['metadata']["NAME"], "Delaware")

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

class UrlTest(unittest.TestCase):
    log = logging.getLogger('UrlTest')
    def test_resolution(self):
        r = get_resolver(None)
        geoids = '10,10001,10002,10003,10001040100'
        extensions = ["html", "csv", "json"]
        geoids = geoids.split(',')
        test = []
        while geoids:
            test.append(geoids.pop())
            geoid_str = ",".join(test)
            for extension in extensions:
                path = "/data/%s.%s" % (geoid_str, extension)
                self.log.debug("asking for %s" % path)
                match = r.resolve(path)
                self.assertEquals(1,len(match.kwargs))
                self.assertEquals(geoid_str,match.kwargs['geoids'])
        
        # A couple paths that should fail.
        self.assertRaises(
            Resolver404,
            r.resolve,
            "/data/10.foo"
        )
        self.assertRaises(
            Resolver404,
            r.resolve,
            "/data/bunk.html"
        )
        
