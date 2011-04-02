"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from unittest import TestCase
from statmodels import Statistic, AggregateStatistic

class StatisticTest(TestCase):
    def test_sums(self):
        """
        Test summing and pct for aggregate statistics
        """
        agg = AggregateStatistic("Aggregate Statistic Label")
        stats = []
        s = Statistic('stat 1',5,10)
        agg.add(s)
        stats.append(s)
        s = Statistic('stat 2',2,5)
        agg.add(s)
        stats.append(s)
        s = Statistic('stat 3',1,2)
        agg.add(s)
        stats.append(s)
        self.assertEqual(8, agg.census2010)
        self.assertEqual(17, agg.census2000)
        self.assertEqual(float(8+17)/17,agg.delta)
        self.assertEqual(len(stats),len(list(agg.children)))
        for orig,kid in zip(stats,agg.children):
            self.assertTrue(orig is kid)
            