#!/usr/bin/env python

from django.utils import unittest

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

    def test_only_complete_geographies(self):
        geos = self.geographies.find({ 'metadata.GEOCOMP': { '$ne': '00' }})
        self.assertEqual(geos.count(), 0)

    def test_state_count(self):
        states = self.geographies.find({ 'sumlev': '040' })

        self.assertEqual(states.count(), 1)
    
    def test_state(self):
        """
        Data import test against known values that Hawaii should have.
        """
        states = self.geographies.find({ 'geoid': config.SUMLEV_STATE })

        self.assertEqual(states.count(), 1)

        state = states[0]

        self.assertEqual(state['sumlev'], config.SUMLEV_STATE)
        self.assertEqual(state['metadata']['NAME'], 'Hawaii')
        self.assertEqual(state['metadata']['STATE'], '15')

        pop_2000 = 1211537
        pop_2010 = 1360301
        self._test_totalpop(state, pop_2000, pop_2010)

    def test_county_count(self):
        counties = self.geographies.find({ 'sumlev': config.SUMLEV_COUNTY })

        self.assertEqual(counties.count(), 5)

    def test_county(self):
        """
        Data import test against known values that Maui County, HI should have.
        """
        counties = self.geographies.find({ 'geoid': '15009' })

        self.assertEqual(counties.count(), 1)

        county = counties[0]

        self.assertEqual(county['sumlev'], config.SUMLEV_COUNTY)
        self.assertEqual(county['metadata']['NAME'], 'Maui County')
        self.assertEqual(county['metadata']['STATE'], '15')
        self.assertEqual(county['metadata']['COUNTY'], '009')

        pop_2000 = 128094 
        pop_2010 = 154834
        self._test_totalpop(county, pop_2000, pop_2010)

    def test_county_subdivision_count(self):
        county_subdivisions = self.geographies.find({ 'sumlev': config.SUMLEV_COUNTY_SUBDIVISION })

        self.assertEqual(county_subdivisions.count(), 44)

    def test_county_subdivision(self):
        """
        Data import test against known values that Hilo CCD County Subdivision, HI should have.
        """
        counties = self.geographies.find({ 'geoid': '1500190630' })

        self.assertEqual(counties.count(), 1)

        county = counties[0]

        self.assertEqual(county['sumlev'], config.SUMLEV_COUNTY_SUBDIVISION)
        self.assertEqual(county['metadata']['NAME'], 'Hilo CCD')
        self.assertEqual(county['metadata']['STATE'], '15')
        self.assertEqual(county['metadata']['COUNTY'], '001')

        pop_2000 = 42425 
        pop_2010 = 45714 
        self._test_totalpop(county, pop_2000, pop_2010)

    def test_place_count(self):
        places = self.geographies.find({ 'sumlev': config.SUMLEV_PLACE })

        self.assertEqual(places.count(), 151)

    def test_place(self):
        """
        Data import test against known values that Pearl City CDP, HI should have.
        """
        places = self.geographies.find({ 'geoid': '1562600' })

        self.assertEqual(places.count(), 1)

        place = places[0]

        self.assertEqual(place['sumlev'], config.SUMLEV_PLACE)
        self.assertEqual(place['metadata']['NAME'], 'Pearl City CDP')
        self.assertEqual(place['metadata']['STATE'], '15')
        self.assertEqual(place['metadata']['PLACE'], '62600')

        pop_2000 = 30976
        pop_2010 = 47698 
        self._test_totalpop(place, pop_2000, pop_2010)

    def test_tract_count(self):
        tracts = self.geographies.find({ 'sumlev': config.SUMLEV_TRACT })

        self.assertEqual(tracts.count(), 351)

    def test_simple_tract(self): 
        """
        Data import test against known values that Tract 405, HI should have.
        """
        tracts = self.geographies.find({ 'geoid': '15007040500' })

        self.assertEqual(tracts.count(), 1)

        tract = tracts[0]

        self.assertEqual(tract['sumlev'], config.SUMLEV_TRACT)
        self.assertEqual(tract['metadata']['NAME'], 'Census Tract 405')
        self.assertEqual(tract['metadata']['STATE'], '15')
        self.assertEqual(tract['metadata']['COUNTY'], '007')

        pop_2000 = 5162 
        pop_2010 = 5943 
        self._test_totalpop(tract, pop_2000, pop_2010)

    def test_block_count(self):
        if config.SUMLEV_BLOCK not in config.SUMLEVS:
            pass
        
        blocks = self.geographies.find({ 'sumlev': config.SUMLEV_BLOCK })

        self.assertEqual(blocks.count(), 25016)

    def test_simple_block(self):
        """
        Data import test against known values for Block 3029 in Tract 210.05, HI.
        
        Note: The test block had the same geography but a different name in 2000.
        It was geoid 150010210011277 in that census.
        """
        if config.SUMLEV_BLOCK not in config.SUMLEVS:
            pass

        blocks = self.geographies.find({ 'geoid': '150010210053029' })

        self.assertEqual(blocks.count(), 1)

        block = blocks[0]

        self.assertEqual(block['sumlev'], config.SUMLEV_BLOCK)
        self.assertEqual(block['metadata']['NAME'], 'Block 3029')
        self.assertEqual(block['metadata']['STATE'], '15')
        self.assertEqual(block['metadata']['COUNTY'], '001')
        self.assertEqual(block['metadata']['TRACT'], '021005')

        pop_2000 = 33 
        pop_2010 = 93 
        self._test_totalpop(block, pop_2000, pop_2010)

class TestTracts(unittest.TestCase):
    def setUp(self):
        self.geographies = utils.get_geography_collection()

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
        tract1_house_2000 = 2269 
        tract1_house_2000_pct = 0.0065
        tract2_house_2000 = 1245
        tract2_house_2000_pct = 0.9938
        tract3_house_2000 = 2991
        tract3_house_2000_pct = 0.0351
        merged_house_2000 = int(sum([
            tract1_house_2000 * tract1_house_2000_pct,
            tract2_house_2000 * tract2_house_2000_pct,
            tract3_house_2000 * tract3_house_2000_pct
        ]))
        merged_house_2010 = 1586 
        merged_house_delta = merged_house_2010 - merged_house_2000
        merged_house_pct_change = float(merged_house_delta) / merged_house_2000

        # Verify that the merged tract is correct
        merged_tract = self.geographies.find({ 'geoid': '15001021402' })
        self.assertEqual(merged_tract.count(), 1)        
        merged_tract = merged_tract[0]

        self.assertEqual(len(merged_tract['xwalk']), 3)
        self.assertAlmostEqual(merged_tract['xwalk']['15001021300']['HUPCT00'], tract1_house_2000_pct)
        self.assertAlmostEqual(merged_tract['xwalk']['15001021400']['HUPCT00'], tract2_house_2000_pct)
        self.assertAlmostEqual(merged_tract['xwalk']['15001021503']['HUPCT00'], tract3_house_2000_pct)

        self.assertEqual(float(merged_tract['data']['2000']['H1']['H001001']), merged_house_2000)
        self.assertEqual(float(merged_tract['data']['2010']['H1']['H001001']), merged_house_2010)
        self.assertEqual(float(merged_tract['data']['delta']['H1']['H001001']), merged_house_delta)
        self.assertAlmostEqual(float(merged_tract['data']['pct_change']['H1']['H001001']), merged_house_pct_change)

class TestBlocks(unittest.TestCase):
    def setUp(self):
        self.geographies = utils.get_geography_collection()

    def test_block_split(self):
        """
        Verify that a split block is crosswalked correctly.
        """
        block1 = self.geographies.find({ 'geoid': '150010210051016' }) 
        self.assertEqual(block1.count(), 1)
        block1 = block1[0]

        split_block_pop = 448 
        block1_land_pct = float(184458) / 587158  # AREALAND_INT / AREALAND_2000
        block1_pop_2000 = int(block1_land_pct * split_block_pop)
        block1_pop_2010 = 22 
        block1_pop_delta = block1_pop_2010 - block1_pop_2000
        block1_pop_pct_change = float(block1_pop_delta) / block1_pop_2000

        self.assertAlmostEqual(block1['xwalk']['150010210011337']['POPPCT00'], block1_land_pct, places=4)
        self.assertAlmostEqual(block1['xwalk']['150010210011337']['HUPCT00'], block1_land_pct, places=4)
        self.assertAlmostEqual(block1['data']['2000']['P1']['P001001'], block1_pop_2000)
        self.assertAlmostEqual(float(block1['data']['2010']['P1']['P001001']), block1_pop_2010)
        self.assertAlmostEqual(float(block1['data']['delta']['P1']['P001001']), block1_pop_delta)
        self.assertAlmostEqual(float(block1['data']['pct_change']['P1']['P001001']), block1_pop_pct_change)

    def test_block_merged(self):
        """
        Verify that a merged block is crosswalked correctly.
        150010210011329 + 150010210011331 -> 150010210051009
        """
        # Compute crosswalked values
        block1_pop_2000 = 12  # 150010210011329
        block2_pop_2000 = 27  # 150010210011331
        merged_pop_2000 = block1_pop_2000 + block2_pop_2000
        merged_pop_2010 = 78 
        merged_pop_delta = merged_pop_2010 - merged_pop_2000
        merged_pop_pct_change = float(merged_pop_delta) / merged_pop_2000

        # Verify that the merged block is correct
        merged_block = self.geographies.find({ 'geoid': '150010210051009' })
        self.assertEqual(merged_block.count(), 1)        
        merged_block = merged_block[0]

        self.assertEqual(len(merged_block['xwalk']), 2)
        self.assertEqual(merged_block['xwalk']['150010210011329']['POPPCT00'], 1.0)
        self.assertEqual(merged_block['xwalk']['150010210011331']['POPPCT00'], 1.0)

        self.assertEqual(float(merged_block['data']['2000']['P1']['P001001']), merged_pop_2000)
        self.assertEqual(float(merged_block['data']['2010']['P1']['P001001']), merged_pop_2010)
        self.assertEqual(float(merged_block['data']['delta']['P1']['P001001']), merged_pop_delta)
        self.assertAlmostEqual(float(merged_block['data']['pct_change']['P1']['P001001']), merged_pop_pct_change)

class TestFieldCrosswalk(unittest.TestCase):
    def setUp(self):
        self.geographies = utils.get_geography_collection()

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
        self.labels = utils.get_label_collection()
        self.geographies = utils.get_geography_collection()

    def test_table_count(self):
        labels = self.labels.find_one({ 'dataset': 'SF1' })

        self.assertEqual(len(labels['tables']), 331)

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
        
    def test_labels_match_geographies(self):
        """
        Hawaii should have a key for every label.
        Every label should have a key for Hawaii.
        """
        geo = self.geographies.find_one({ 'geoid': '15' })
        labels = self.labels.find_one({ 'dataset': 'SF1' })

        geo_tables = geo['data']['2010']
        labels_tables = labels['tables']

        self.assertEqual(sorted(geo_tables.keys()), sorted(labels_tables.keys()))

        # Test table has labels
        for table_name, geo_keys in geo_tables.items():
            label_keys = labels_tables[table_name]['labels']

            self.assertEqual(sorted(geo_keys.keys()), sorted(label_keys.keys()))

        for table_name, label_data in labels_tables.items():
            label_keys = label_data['labels']
            geo_keys = geo_tables[table_name]

            self.assertEqual(sorted(geo_keys.keys()), sorted(label_keys.keys()))

    def test_table_sizes(self):
        """
        Test that the tables documented size matches its actual label count.
        """
        labels_tables = self.labels.find_one({ 'dataset': 'SF1' })['tables']

        for label_data in labels_tables.values():
            self.assertEqual(label_data['size'], len(label_data['labels']))

if __name__ == '__main__':
    unittest.main()
        
