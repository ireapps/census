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
