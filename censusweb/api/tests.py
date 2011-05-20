"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.utils import unittest
from statmodels import Statistic, AggregateStatistic, ssf, sumsf

class StatisticTest(unittest.TestCase):
    def test_sums(self):
        """
        Test summing and pct for aggregate statistics
        """
        agg = AggregateStatistic("Aggregate Statistic Label")
        stats = []
        s = Statistic('stat 1',census2010=5,census2000=10)
        agg.add(s)
        stats.append(s)

        s = Statistic('stat 2',census2000=5,census2010=2)
        agg.add(s)
        stats.append(s)

        s = Statistic('stat 3',census2010=1,census2000=2)
        agg.add(s)
        stats.append(s)

        s = Statistic('stat 4 non-atomic',census2010=1000,census2000=10,atomic=False)
        agg.add(s)
        stats.append(s)

        s = Statistic('stat 4 non-atomic',census2010=100,census2000=50,atomic=False)
        agg.add(s)
        stats.append(s)

        self.assertEqual(8, agg.census2010)
        self.assertEqual(17, agg.census2000)
        self.assertEqual(float(8+17)/17,agg.delta)
        self.assertEqual(len(stats),len(list(agg.children)))
        for orig,kid in zip(stats,agg.children):
            self.assertTrue(kid.label,orig is kid)

    def test_deltas(self):
        s = Statistic('stat 1',census2010=10,census2000=5)
        self.assertEqual(1.0,s.delta)

        s = Statistic('stat 2',census2010=5,census2000=10)
        self.assertEqual(-.5,s.delta)


    def test_indent(self):
        agg = AggregateStatistic("Aggregate Statistic Label")
        stats = []
        s = Statistic('stat 1',census2010=5,census2000=10)
        agg.add(s)
        stats.append(s)

        s = Statistic('stat 2',census2000=5,census2010=2)
        agg.add(s)
        stats.append(s)

        s = Statistic('stat 3',census2010=1,census2000=2)
        agg.add(s)
        stats.append(s)

        self.assertEqual(0, agg.indent)
        for kid in agg.children:
            self.assertEqual(agg.indent + 1, kid.indent)
            
    def test_ssf(self):
        "Test ssf (SimpleStatisticFactory)"
        label = 'my label'
        column = 'col'
        factory = ssf(label, column)
        s = factory(census2010={column: 5})
        self.assertTrue(type(s) == Statistic)
        self.assertEqual(label, s.label)
        self.assertEqual(5,s.census2010)
        self.assertTrue(s.census2000 is None)
        
    def test_sumsf(self):
        "test sumsf (SummingStatisticFactory)"
        label = 'another label'
        columns = ['col1', 'col2', 'col3']
        factory = sumsf(label, columns)
        s = factory(census2010={'col1': 5, 'col2': 3, 'col3': 1, 'col4': 0})
        self.assertTrue(type(s) == Statistic)
        self.assertEqual(label, s.label)
        self.assertEqual(9,s.census2010)
        self.assertTrue(s.census2000 is None)
