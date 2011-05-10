#!/usr/bin/env python

import unittest

from pymongo import Connection

import config

class TestSimpleGeographies(unittest.TestCase):
    def setUp(self):
        connection = Connection()
        db = connection[config.CENSUS_DB]
        self.geographies = db[config.GEOGRAPHIES_COLLECTION]

    def test_nation(self):
        # TODO
        pass
    
    def test_state(self):
        states = self.geographies.find({ 'geoid': '10' })

        self.assertEqual(states.count(), 1)

        state = states[0]

        self.assertEqual(state['sumlev'], '040')
        self.assertEqual(state['metadata']['NAME'], 'Delaware')

    def test_county(self):
        # TODO
        pass
    
    def test_place(self):
        # TODO
        pass

class TestTracts(unittest.TestCase):
    def setUp(self):
        connection = Connection()
        db = connection[config.CENSUS_DB]
        self.geographies = db[config.GEOGRAPHIES_COLLECTION]

    def test_simple_tract(self):
        # TODO
        pass

class TestLabels(unittest.TestCase):
    def setUp(self):
        connection = Connection()
        db = connection[config.CENSUS_DB]
        self.labels = db[config.LABELS_COLLECTION]

    def test_table(self):
        """
        Header rows from input file:
        "P4.  HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER [73]","",""
        "Universe: Total population 18 years and over","",""
        """
        table = self.labels.find_one({ 'key': 'P4', 'year': '2010' })

        self.assertEqual(table['name'], 'HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER')
        self.assertEqual(table['size'], 73)
        self.assertEqual(table['universe'], 'Total population 18 years and over')

    def test_label(self):
        """
        Rows from input file:
        "      Population of four races:","P0020049"," P1"
        "        White; Black or African American; American Indian and Alaska Native; Asian","P0020050"," P1"
        """
        table = self.labels.find_one({ 'key': 'P2', 'year': '2010' })
        label = table['labels']['P0020050']

        self.assertEqual(label['text'], 'White; Black or African American; American Indian and Alaska Native; Asian')
        self.assertEqual(label['parent'], 'P0020049')
        self.assertEqual(label['indent'], 4)
        
if __name__ == '__main__':
    unittest.main()
        
