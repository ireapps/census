#!/usr/bin/env python

from django.utils import unittest
from pymongo import Connection

import config

class TestSimpleGeographies(unittest.TestCase):
    def setUp(self):
        connection = Connection()
        db = connection[config.CENSUS_DB]
        self.geographies = db[config.GEOGRAPHIES_COLLECTION]

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

    @unittest.skip('TODO')
    def test_state_count(self):
        states = self.geographies.find({ 'sumlev': '15' })
    
    def test_state(self):
        """
        Data import test against known values that Hawaii should have.
        """
        states = self.geographies.find({ 'geoid': '15' })

        self.assertEqual(states.count(), 1)

        state = states[0]

        self.assertEqual(state['sumlev'], '040')
        self.assertEqual(state['metadata']['NAME'], 'Hawaii')
        self.assertEqual(state['metadata']['STATE'], '15')

        pop_2000 = 1211537
        pop_2010 = 1360301
        self._test_totalpop(state, pop_2000, pop_2010)

    @unittest.skip('TODO')
    def test_county_count(self):
        pass

    def test_county(self):
        """
        Data import test against known values that Maui County, HI should have.
        """
        counties = self.geographies.find({ 'geoid': '15009' })

        self.assertEqual(counties.count(), 1)

        county = counties[0]

        self.assertEqual(county['sumlev'], '050')
        self.assertEqual(county['metadata']['NAME'], 'Maui County')
        self.assertEqual(county['metadata']['STATE'], '15')
        self.assertEqual(county['metadata']['COUNTY'], '009')

        pop_2000 = 128094 
        pop_2010 = 154834
        self._test_totalpop(county, pop_2000, pop_2010)

    @unittest.skip('TODO')
    def test_county_subdivision_count(self):
        pass

    @unittest.skip('TODO')
    def test_county_subdivision(self):
        pass

    @unittest.skip('TODO')
    def test_place_count(self):
        pass

    def test_place(self):
        """
        Data import test against known values that Pearl City CDP, HI should have.
        """
        places = self.geographies.find({ 'geoid': '1562600' })

        self.assertEqual(places.count(), 1)

        place = places[0]

        self.assertEqual(place['sumlev'], '160')
        self.assertEqual(place['metadata']['NAME'], 'Pearl City CDP')
        self.assertEqual(place['metadata']['STATE'], '15')
        self.assertEqual(place['metadata']['PLACE'], '62600')

        pop_2000 = 30976
        pop_2010 = 47698 
        self._test_totalpop(place, pop_2000, pop_2010)

    @unittest.skip('TODO')
    def test_tract_count(self):
        pass

    def test_simple_tract(self): 
        """
        Data import test against known values that Tract 405, HI should have.
        """
        tracts = self.geographies.find({ 'geoid': '15007040500' })

        self.assertEqual(tracts.count(), 1)

        tract = tracts[0]

        self.assertEqual(tract['sumlev'], '140')
        self.assertEqual(tract['metadata']['NAME'], 'Census Tract 405')
        self.assertEqual(tract['metadata']['STATE'], '15')
        self.assertEqual(tract['metadata']['COUNTY'], '007')

        pop_2000 = 5162 
        pop_2010 = 5943 
        self._test_totalpop(tract, pop_2000, pop_2010)

class TestTracts(unittest.TestCase):
    def setUp(self):
        connection = Connection()
        db = connection[config.CENSUS_DB]
        self.geographies = db[config.GEOGRAPHIES_COLLECTION]

    def test_tract_split(self):
        """
        Verify that a split tract is crosswalked correctly.
        """
        # Check that split tract does not exist in 2010
        split_tract = self.geographies.find({ 'geoid': '15003003500' })
        self.assertEqual(split_tract.count(), 0)

        # Validate first new tract from the split tract
        # Tract 35.01
        tract1 = self.geographies.find({ 'geoid': '15003003501' })
        self.assertEqual(tract1.count(), 1)
        tract1 = tract1[0]
        
        split_tract_pop_2000 = 5834
        tract1_pop_pct = 0.3706 
        tract1_pop_2000 = int(tract1_pop_pct * split_tract_pop_2000)
        tract1_pop_2010 = 2282 
        tract1_pop_delta = tract1_pop_2010 - tract1_pop_2000
        tract1_pop_pct_change = float(tract1_pop_delta) / tract1_pop_2000

        self.assertAlmostEqual(tract1['xwalk']['15003003500']['POPPCT00'], tract1_pop_pct, places=4)
        self.assertAlmostEqual(tract1['data']['2000']['P1']['P001001'], tract1_pop_2000)
        self.assertAlmostEqual(float(tract1['data']['2010']['P1']['P001001']), tract1_pop_2010)
        self.assertAlmostEqual(float(tract1['data']['delta']['P1']['P001001']), tract1_pop_delta)
        self.assertAlmostEqual(float(tract1['data']['pct_change']['P1']['P001001']), tract1_pop_pct_change)
        
        # Validate second new part from the split tract
        # Tract 35.02
        tract2 = self.geographies.find({ 'geoid': '15003003502' })
        self.assertEqual(tract2.count(), 1)
        tract2 = tract2[0]

        tract2_pop_pct = 0.6294
        tract2_pop_2000 = int(tract2_pop_pct * split_tract_pop_2000)
        tract2_pop_2010 = 3876
        tract2_pop_delta = tract2_pop_2010 - tract2_pop_2000
        tract2_pop_pct_change = float(tract2_pop_delta) / tract2_pop_2000 
        
        self.assertAlmostEqual(tract2['xwalk']['15003003500']['POPPCT00'], tract2_pop_pct, places=4)
        self.assertAlmostEqual(tract2['data']['2000']['P1']['P001001'], tract2_pop_2000)
        self.assertAlmostEqual(float(tract2['data']['2010']['P1']['P001001']), tract2_pop_2010)
        self.assertAlmostEqual(float(tract2['data']['delta']['P1']['P001001']), tract2_pop_delta)
        self.assertAlmostEqual(float(tract2['data']['pct_change']['P1']['P001001']), tract2_pop_pct_change)

        # Verify that no other tracts got crosswalk allocations from the split tract
        allocated = self.geographies.find({ 'xwalk.15003003500': { '$exists': True } })
        self.assertEqual(allocated.count(), 2)

    def test_tract_split_housing(self):
        """
        Verify that a split tract is crosswalked correctly.
        """
        # Validate first new tract from the split tract
        # Tract 35.01
        tract1 = self.geographies.find({ 'geoid': '15003003501' })
        self.assertEqual(tract1.count(), 1)
        tract1 = tract1[0]
        
        split_tract_house_2000 = 3370 
        tract1_house_pct = 0.383 
        tract1_house_2000 = int(tract1_house_pct * split_tract_house_2000)
        tract1_house_2010 = 1353 
        tract1_house_delta = tract1_house_2010 - tract1_house_2000
        tract1_house_pct_change = float(tract1_house_delta) / tract1_house_2000

        self.assertAlmostEqual(tract1['xwalk']['15003003500']['HUPCT00'], tract1_house_pct, places=4)
        self.assertAlmostEqual(tract1['data']['2000']['H1']['H001001'], tract1_house_2000)
        self.assertAlmostEqual(float(tract1['data']['2010']['H1']['H001001']), tract1_house_2010)
        self.assertAlmostEqual(float(tract1['data']['delta']['H1']['H001001']), tract1_house_delta)
        self.assertAlmostEqual(float(tract1['data']['pct_change']['H1']['H001001']), tract1_house_pct_change)

        # Validate second new part from the split tract
        # Tract 35.02
        tract2 = self.geographies.find({ 'geoid': '15003003502' })
        self.assertEqual(tract2.count(), 1)
        tract2 = tract2[0]

        tract2_house_pct = 0.617
        tract2_house_2000 = int(tract2_house_pct * split_tract_house_2000)
        tract2_house_2010 = 2180 
        tract2_house_delta = tract2_house_2010 - tract2_house_2000
        tract2_house_pct_change = float(tract2_house_delta) / tract2_house_2000 
        
        self.assertAlmostEqual(tract2['xwalk']['15003003500']['HUPCT00'], tract2_house_pct, places=4)
        self.assertAlmostEqual(tract2['data']['2000']['H1']['H001001'], tract2_house_2000)
        self.assertAlmostEqual(float(tract2['data']['2010']['H1']['H001001']), tract2_house_2010)
        self.assertAlmostEqual(float(tract2['data']['delta']['H1']['H001001']), tract2_house_delta)
        self.assertAlmostEqual(float(tract2['data']['pct_change']['H1']['H001001']), tract2_house_pct_change)

    def test_tract_merged(self):
        """
        Verify that a merged tract is crosswalked correctly.

        TODO - test housing
        """
        # Verify that the first dissolved tract no longer exists
        tract1 = self.geographies.find({ 'geoid': '15003008607' })
        self.assertEqual(tract1.count(), 0)

        tract2 = self.geographies.find({ 'geoid': '15003008608' })
        self.assertEqual(tract2.count(), 0)

        tract3 = self.geographies.find({ 'geoid': '15003008500' })
        self.assertEqual(tract3.count(), 0)

        # Compute crosswalked values
        tract1_pop_2000 = 1544 
        tract2_pop_2000 = 0 
        tract3_pop_2000 = 1311
        merged_pop_2000 = tract1_pop_2000 # only this tract contributed population
        merged_pop_2010 = 5493 
        merged_pop_delta = merged_pop_2010 - merged_pop_2000
        merged_pop_pct_change = float(merged_pop_delta) / merged_pop_2000

        # Verify that the merged tract is correct
        merged_tract = self.geographies.find({ 'geoid': '15003011500' })
        self.assertEqual(merged_tract.count(), 1)        
        merged_tract = merged_tract[0]

        self.assertEqual(len(merged_tract['xwalk']), 3)
        self.assertEqual(merged_tract['xwalk']['15003008607']['POPPCT00'], 1.0)
        self.assertEqual(merged_tract['xwalk']['15003008608']['POPPCT00'], 1.0)
        self.assertEqual(merged_tract['xwalk']['15003008500']['POPPCT00'], 0.0)

        self.assertEqual(float(merged_tract['data']['2000']['P1']['P001001']), merged_pop_2000)
        self.assertEqual(float(merged_tract['data']['2010']['P1']['P001001']), merged_pop_2010)
        self.assertEqual(float(merged_tract['data']['delta']['P1']['P001001']), merged_pop_delta)
        self.assertAlmostEqual(float(merged_tract['data']['pct_change']['P1']['P001001']), merged_pop_pct_change)
        
        self.assertEqual(merged_tract['xwalk']['15003008607']['HUPCT00'], 1.0)
        self.assertEqual(merged_tract['xwalk']['15003008608']['HUPCT00'], 1.0)
        self.assertEqual(merged_tract['xwalk']['15003008500']['HUPCT00'], 0.0)

    def test_tract_complex_merge(self):
        # Verify state of 2010 status of tracts which contributed to the merged tract
        tract1 = self.geographies.find({ 'geoid': '15001021300' })
        self.assertEqual(tract1.count(), 1)

        tract2 = self.geographies.find({ 'geoid': '15001021400' })
        self.assertEqual(tract2.count(), 0)

        tract3 = self.geographies.find({ 'geoid': '15001021503' })
        self.assertEqual(tract3.count(), 0)

        # Compute crosswalked values
        tract1_house_2000 = 2768
        tract1_house_2000_pct = 0.007
        tract2_house_2000 = 1456
        tract2_house_2000_pct = 0.9932
        tract3_house_2000 = 3447
        tract3_house_2000_pct = 0.0579
        merged_house_2000 = sum([
            tract1_house_2000 * tract1_house_2000_pct,
            tract2_house_2000 * tract2_house_2000_pct,
            tract3_house_2000 * tract3_house_2000_pct
        ])
        merged_house_2010 = 1586 
        merged_house_delta = merged_house_2010 - merged_house_2000
        merged_house_pct_change = float(merged_house_delta) / merged_house_2000

        # Verify that the merged tract is correct
        merged_tract = self.geographies.find({ 'geoid': '15001021402' })
        self.assertEqual(merged_tract.count(), 1)        
        merged_tract = merged_tract[0]

        self.assertEqual(len(merged_tract['xwalk']), 3)
        self.assertEqual(merged_tract['xwalk']['15001021300']['HUPCT00'], tract1_house_2000_pct)
        self.assertEqual(merged_tract['xwalk']['15001021400']['HUPCT00'], tract2_house_2000_pct)
        self.assertEqual(merged_tract['xwalk']['15001021503']['HUPCT00'], tract3_house_2000_pct)

        self.assertEqual(float(merged_tract['data']['2000']['P1']['P001001']), merged_house_2000)
        self.assertEqual(float(merged_tract['data']['2010']['P1']['P001001']), merged_house_2010)
        self.assertEqual(float(merged_tract['data']['delta']['P1']['P001001']), merged_house_delta)
        self.assertAlmostEqual(float(merged_tract['data']['pct_change']['P1']['P001001']), merged_house_pct_change)

class TestFieldCrosswalk(unittest.TestCase):
    def setUp(self):
        connection = Connection()
        db = connection[config.CENSUS_DB]
        self.geographies = db[config.GEOGRAPHIES_COLLECTION]

    def test_exact_same_name(self):
        state = self.geographies.find_one({ 'geoid': '15' })

        urban_and_rural_pop_2000 = 1211537
        urban_and_rural_pop_2010 = 1360301
        delta = urban_and_rural_pop_2010 - urban_and_rural_pop_2000
        pct_change = float(urban_and_rural_pop_2010 - urban_and_rural_pop_2000) / urban_and_rural_pop_2000

        self.assertEqual(float(state['data']['2000']['P2']['P002001']), urban_and_rural_pop_2000)
        self.assertEqual(float(state['data']['2010']['P2']['P002001']), urban_and_rural_pop_2010)
        self.assertEqual(float(state['data']['delta']['P2']['P002001']), delta)
        self.assertAlmostEqual(float(state['data']['pct_change']['P2']['P002001']), pct_change)

    def test_different_tables(self):
        state = self.geographies.find_one({ 'geoid': '15' })

        pacific_islanders_2000 = 113539
        pacific_islanders_2010 = 135422
        delta = pacific_islanders_2010 - pacific_islanders_2000
        pct_change = float(pacific_islanders_2010 - pacific_islanders_2000) / pacific_islanders_2000

        # 2000 field P007006
        self.assertEqual(float(state['data']['2000']['P3']['P003006']), pacific_islanders_2000)
        self.assertEqual(float(state['data']['2010']['P3']['P003006']), pacific_islanders_2010)
        self.assertEqual(float(state['data']['delta']['P3']['P003006']), delta)
        self.assertAlmostEqual(float(state['data']['pct_change']['P3']['P003006']), pct_change)

    def test_different_everything(self):
        state = self.geographies.find_one({ 'geoid': '15' })

        unmarried_partner_households_2000 = 23516 
        unmarried_partner_households_2010 = 33068 
        delta = unmarried_partner_households_2010 - unmarried_partner_households_2000
        pct_change = float(unmarried_partner_households_2010 - unmarried_partner_households_2000) / unmarried_partner_households_2000

        # 2000 field PCT014002
        self.assertEqual(float(state['data']['2000']['PCT15']['PCT015013']), unmarried_partner_households_2000)
        self.assertEqual(float(state['data']['2010']['PCT15']['PCT015013']), unmarried_partner_households_2010)
        self.assertEqual(float(state['data']['delta']['PCT15']['PCT015013']), delta)
        self.assertAlmostEqual(float(state['data']['pct_change']['PCT15']['PCT015013']), pct_change)

class TestLabels(unittest.TestCase):
    def setUp(self):
        connection = Connection()
        db = connection[config.LABELS_DB]
        self.labels = db[config.LABELS_COLLECTION]

    @unittest.skip('TODO')
    def test_table_count(self):
        pass

    def test_table(self):
        """
        Header rows from input file:
        P12F.,,0,SEX BY AGE (SOME OTHER RACE ALONE) [49],,,,,,,,2000 SF1 P12F.
        P12F.,,0,Universe:  People who are Some Other Race alone,,,,,,,,
        """
        table = self.labels.find_one({ 'dataset': 'SF1' })['tables']['P12F']

        self.assertEqual(table['name'], 'SEX BY AGE (SOME OTHER RACE ALONE)')
        self.assertEqual(table['size'], 49)
        self.assertEqual(table['universe'], 'People who are Some Other Race alone')

    def test_label(self):
        """
        P12F.,1,0,Total:,,,,,,,,
        """
        table = self.labels.find_one({ 'dataset': 'SF1' })['tables']['P12F']
        label = table['labels']['P012F001']

        self.assertEqual(label['text'], 'Total:')
        self.assertEqual(label['parent'], None)
        self.assertEqual(label['indent'], 0)
        
if __name__ == '__main__':
    unittest.main()
        
