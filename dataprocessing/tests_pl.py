#!/usr/bin/env python

from django.utils import unittest
from pymongo import Connection

import config
import utils

class TestSimpleGeographies(unittest.TestCase):
    def setUp(self):
        self.geographies = utils.get_geography_collection()

    def _test_totalpop(self, obj, known_2000, known_2010):
        """
        Shortcut to test "total population" field from the P1 (race)
        table since this table exists for both 2000 and 2010.
        """
        known_delta = known_2010 - known_2000
        known_pct = float(known_delta) / float(known_2000)

        self.assertEqual(float(obj['data']['2000']["P1"]['P001001']), known_2000)
        self.assertEqual(float(obj['data']['2010']["P1"]['P001001']), known_2010)
        self.assertEqual(float(obj['data']['delta']["P1"]['P001001']), known_delta)
        self.assertAlmostEqual(
            float(obj['data']['pct_change']["P1"]['P001001']),
            known_pct
        )

    # TODO 
    #def test_nation(self):
    #    pass
    
    def test_state(self):
        """
        Data import test against known values that Delaware should have.
        """
        states = self.geographies.find({ 'geoid': '10' })

        self.assertEqual(states.count(), 1)

        state = states[0]

        self.assertEqual(state['sumlev'], '040')
        self.assertEqual(state['metadata']['NAME'], 'Delaware')
        self.assertEqual(state['metadata']['STATE'], '10')

        pop_2000 = 783600
        pop_2010 = 897934
        self._test_totalpop(state, pop_2000, pop_2010)

    def test_county(self):
        """
        Data import test against known values that Kent County, DE should have.
        """
        counties = self.geographies.find({ 'geoid': '10001' })

        self.assertEqual(counties.count(), 1)

        county = counties[0]

        self.assertEqual(county['sumlev'], '050')
        self.assertEqual(county['metadata']['NAME'], 'Kent County')
        self.assertEqual(county['metadata']['STATE'], '10')
        self.assertEqual(county['metadata']['COUNTY'], '001')

        pop_2000 = 126697
        pop_2010 = 162310
        self._test_totalpop(county, pop_2000, pop_2010)

    def test_place(self):
        """
        Data import test against known values that Newark city, DE should have.
        """
        places = self.geographies.find({ 'geoid': '1050670' })

        self.assertEqual(places.count(), 1)

        place = places[0]

        self.assertEqual(place['sumlev'], '160')
        self.assertEqual(place['metadata']['NAME'], 'Newark city')
        self.assertEqual(place['metadata']['STATE'], '10')
        self.assertEqual(place['metadata']['PLACE'], '50670')

        pop_2000 = 28547
        pop_2010 = 31454
        self._test_totalpop(place, pop_2000, pop_2010)

    def test_simple_tract(self): 
        """
        Data import test against known values that Tract 401, Kent County, DE should have.
        """
        tracts = self.geographies.find({ 'geoid': '10001040100' })

        self.assertEqual(tracts.count(), 1)

        tract = tracts[0]

        self.assertEqual(tract['sumlev'], '140')
        self.assertEqual(tract['metadata']['NAME'], 'Census Tract 401')
        self.assertEqual(tract['metadata']['STATE'], '10')
        self.assertEqual(tract['metadata']['COUNTY'], '001')

        pop_2000 = 5337
        pop_2010 = 6541
        self._test_totalpop(tract, pop_2000, pop_2010)

class TestTracts(unittest.TestCase):
    def setUp(self):
        self.geographies = utils.get_geography_collection()

    def test_tract_split(self):
        """
        Verify that a split tract is crosswalked correctly.
        """
        # Check that split tract does not exist in 2010
        split_tract = self.geographies.find({ 'geoid': '10003013902' })
        self.assertEqual(split_tract.count(), 0)

        # Validate first new tract from the split tract
        # Tract 139.03
        tract1 = self.geographies.find({ 'geoid': '10003013903' })
        self.assertEqual(tract1.count(), 1)
        tract1 = tract1[0]
        
        split_tract_pop_2000 = 10405
        tract1_pop_pct = 0.3904
        tract1_pop_2000 = int(tract1_pop_pct * split_tract_pop_2000)
        tract1_pop_2010 = 4983 
        tract1_pop_delta = tract1_pop_2010 - tract1_pop_2000
        tract1_pop_pct_change = float(tract1_pop_delta) / tract1_pop_2000

        self.assertAlmostEqual(tract1['xwalk']['10003013902']['POPPCT00'], tract1_pop_pct, places=4)
        self.assertAlmostEqual(tract1['data']['2000']['P1']['P001001'], tract1_pop_2000)
        self.assertAlmostEqual(tract1['data']['2010']['P1']['P001001'], tract1_pop_2010)
        self.assertAlmostEqual(float(tract1['data']['delta']['P1']['P001001']), tract1_pop_delta)
        self.assertAlmostEqual(float(tract1['data']['pct_change']['P1']['P001001']), tract1_pop_pct_change)
        
        # Validate second new part from the split tract
        # Tract 139.04
        tract2 = self.geographies.find({ 'geoid': '10003013904' })
        self.assertEqual(tract2.count(), 1)
        tract2 = tract2[0]

        tract2_pop_pct = 0.6096
        tract2_pop_2000 = int(tract2_pop_pct * split_tract_pop_2000)
        tract2_pop_2010 = 7780
        tract2_pop_delta = tract2_pop_2010 - tract2_pop_2000
        tract2_pop_pct_change = float(tract2_pop_delta) / tract2_pop_2000 
        
        self.assertAlmostEqual(tract2['xwalk']['10003013902']['POPPCT00'], tract2_pop_pct, places=4)
        self.assertAlmostEqual(tract2['data']['2000']['P1']['P001001'], tract2_pop_2000)
        self.assertAlmostEqual(tract2['data']['2010']['P1']['P001001'], tract2_pop_2010)
        self.assertAlmostEqual(float(tract2['data']['delta']['P1']['P001001']), tract2_pop_delta)
        self.assertAlmostEqual(float(tract2['data']['pct_change']['P1']['P001001']), tract2_pop_pct_change)

        # Verify that no other tracts got crosswalk allocations from the split tract
        allocated = self.geographies.find({ 'xwalk.10003013902': { '$exists': True } })
        self.assertEqual(allocated.count(), 2)

    @unittest.skip('This test doesn\'t work because there was no H1 table in 2000')
    def test_tract_split_housing(self):
        """
        Verify that a split tract is crosswalked correctly.
        """
        # Validate first new tract from the split tract
        # Tract 139.03
        tract1 = self.geographies.find({ 'geoid': '10003013903' })
        self.assertEqual(tract1.count(), 1)
        tract1 = tract1[0]
        
        split_tract_house_2000 = None
        tract1_house_pct = 0.3431 
        tract1_house_2000 = int(tract1_house_pct * split_tract_house_2000)
        tract1_house_2010 = 1671 
        tract1_house_delta = tract1_house_2010 - tract1_house_2000
        tract1_house_pct_change = float(tract1_house_delta) / tract1_house_2000

        self.assertAlmostEqual(tract1['xwalk']['10003013902']['HUPCT00'], tract1_house_pct, places=4)
        self.assertAlmostEqual(tract1['data']['2000']['H1']['H001001'], tract1_house_2000)
        self.assertAlmostEqual(tract1['data']['2010']['H1']['H001001'], tract1_house_2010)
        self.assertAlmostEqual(float(tract1['data']['delta']['H1']['H001001']), tract1_house_delta)
        self.assertAlmostEqual(float(tract1['data']['pct_change']['H1']['H001001']), tract1_house_pct_change)

        # Validate second new part from the split tract
        # Tract 139.04
        tract2 = self.geographies.find({ 'geoid': '10003013904' })
        self.assertEqual(tract2.count(), 1)
        tract2 = tract2[0]

        tract2_house_pct = 0.6569
        tract2_house_2000 = int(tract2_house_pct * split_tract_house_2000)
        tract2_house_2010 = 3199 
        tract2_house_delta = tract2_house_2010 - tract2_house_2000
        tract2_house_pct_change = float(tract2_house_delta) / tract2_house_2000 
        
        self.assertAlmostEqual(tract2['xwalk']['10003013902']['HUPCT00'], tract2_house_pct, places=4)
        self.assertAlmostEqual(tract2['data']['2000']['H1']['H001001'], tract2_house_2000)
        self.assertAlmostEqual(tract2['data']['2010']['H1']['H001001'], tract2_house_2010)
        self.assertAlmostEqual(float(tract2['data']['delta']['H1']['PH001001']), tract2_house_delta)
        self.assertAlmostEqual(float(tract2['data']['pct_change']['H1']['H001001']), tract2_house_pct_change)

    def test_tract_merged(self):
        """
        Verify that a merged tract is crosswalked correctly.

        TODO - test housing
        """
        # Verify that the first dissolved tract no longer exists
        tract1 = self.geographies.find({ 'geoid': '10001040600' })
        self.assertEqual(tract1.count(), 0)

        tract2 = self.geographies.find({ 'geoid': '10001040800' })
        self.assertEqual(tract2.count(), 0)

        # Compute crosswalked values
        tract1_pop_2000 = 2380 
        tract2_pop_2010 = 2770
        merged_pop_2000 = tract1_pop_2000 + tract2_pop_2010
        merged_pop_2010 = 6131
        merged_pop_delta = merged_pop_2010 - merged_pop_2000
        merged_pop_pct_change = float(merged_pop_delta) / merged_pop_2000

        # Verify that the merged tract is correct
        merged_tract = self.geographies.find({ 'geoid': '10001043300' })
        self.assertEqual(merged_tract.count(), 1)        
        merged_tract = merged_tract[0]

        self.assertEqual(len(merged_tract['xwalk']), 2)
        self.assertEqual(merged_tract['xwalk']['10001040600']['POPPCT00'], 1.0)
        self.assertEqual(merged_tract['xwalk']['10001040800']['POPPCT00'], 1.0)

        self.assertEqual(merged_tract['data']['2000']['P1']['P001001'], merged_pop_2000)
        self.assertEqual(merged_tract['data']['2010']['P1']['P001001'], merged_pop_2010)
        self.assertEqual(float(merged_tract['data']['delta']['P1']['P001001']), merged_pop_delta)
        self.assertAlmostEqual(float(merged_tract['data']['pct_change']['P1']['P001001']), merged_pop_pct_change)
        
        self.assertEqual(merged_tract['xwalk']['10001040600']['HUPCT00'], 1.0)
        self.assertEqual(merged_tract['xwalk']['10001040800']['HUPCT00'], 1.0)

class TestLabels(unittest.TestCase):
    def setUp(self):
        self.labels = utils.get_label_collection()

    def test_table(self):
        """
        Header rows from input file:
        "P4.  HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER [73]","",""
        "Universe: Total population 18 years and over","",""
        """
        table = self.labels.find_one({ 'dataset': 'PL' })['tables']['P4']

        self.assertEqual(table['name'], 'HISPANIC OR LATINO, AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER')
        self.assertEqual(table['size'], 73)
        self.assertEqual(table['universe'], 'Total population 18 years and over')

    def test_label(self):
        """
        Rows from input file:
        "      Population of four races:","P0020049"," P1"
        "        White; Black or African American; American Indian and Alaska Native; Asian","P0020050"," P1"
        """
        table = self.labels.find_one({ 'dataset': 'PL' })['tables']['P2']
        label = table['labels']['P0020050']

        self.assertEqual(label['text'], 'White; Black or African American; American Indian and Alaska Native; Asian')
        self.assertEqual(label['parent'], 'P0020049')
        self.assertEqual(label['indent'], 4)
        
if __name__ == '__main__':
    unittest.main()
        
