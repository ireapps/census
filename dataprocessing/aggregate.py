#!/usr/bin/env python

"""
How to use aggregate census data to arbitrary geographies:

* Update config.py, adding SUMLEV_BLOCK to the list of summary levels to be loaded. Example:

    SUMLEVS = [SUMLEV_BLOCK]

* Optionally, alse in config.py update the filter_geographies() function to reduce the data to a one or more counties. Example:

    def filter_geographies(row_dict):
        return row_dict['COUNTY'] == '003'

* Load the data for your state. Example:

    ./batch_sf.sh Hawaii staging

* Download the 2000 (NOT 2010) block-level shapefile for your state (or county), unzip it, and copy the enclosed .dbf file somewhere convenient. You can delete the rest.

* If it isn't already, convert the shapefile you will be aggregating by into 4269 projection. Example:

    ogr2ogr -f "ESRI Shapefile" wards4269 -t_srs EPSG:4269 wards

* Run this aggregation script, providing the following parameters: the .dbf you just extracted, the shapefile you want to aggregate by, a name for the new summary level. Optionally you may also provide the name of an column in the .dbf to use as a unique id. Example:

    ./aggregate.py tl_2010_15003_tabblock00.dbf wards/wards.shp ward WARD_ID 

* Rerun the crosswalk and compute_deltas scripts, limiting them to only the summary level you just created. Example:

    ./crosswalk ward
    ./compute_deltas ward

* You now have arbitrarily aggregated geographies in your Mongo database.
"""

import sys

import dbf
from osgeo import ogr

import config
import utils

if len(sys.argv) < 2:
    sys.exit('You must provide a DBF file for the 2000 blocks that will be aggregated, a shapefile to aggregate by, and a name for the new summary level. You may optionally provide the name of a field within the shapefile to use as the unique ID.')

BLOCKS_DBF = sys.argv[1]
SHAPEFILE = sys.argv[2]
NEW_SUMLEV = sys.argv[3]

if len(sys.argv) == 5:
    ID_FIELD = sys.argv[4]
else:
    ID_FIELD = None

shapes = ogr.Open(SHAPEFILE)
shapes_layer = shapes[0]

def load_2000_block_points(filename):
    """
    Builds a dictionary of internal points from the DBF associated with a
    shapefile of 2000 blocks (the 2010 release of those blocks).

    This works around inaccuracies in the internal points embedded in the
    2000 geoheaders.
    """
    table = dbf.Table(filename)
    points = {}

    for row in table:
        points[row['blkidfp00']] = {
            'lat': float(row['intptlat00']),
            'lon': float(row['intptlon00']),
        }

    print 'Loaded %i points from %s' % (len(points), filename)

    return points

def find_geometry_containing_point(lat, lon):
    """
    Iterate over all aggregating geometries to see if any contain the given point.
    """
    shapes_layer.ResetReading()

    point = ogr.Geometry(ogr.wkbPoint)
    point.SetPoint_2D(0, lon, lat)

    for feature in shapes_layer:
        geometry = feature.GetGeometryRef()

        if geometry.Contains(point):
            if ID_FIELD:
                return feature.GetField(ID_FIELD)

            return feature.GetFID()

    return None

def make_custom_geoid(sumlev, feature_id):
    """
    Generate a unique geoid for the given feature.
    """
    return '%s_%s' % (sumlev, feature_id)

def aggregate_geographies(collection, dataset, points=None):
    """
    Aggregate geographies in the given collection.
    """
    print 'Aggregating collection "%s"' % collection.name

    collection.remove({ 'sumlev': NEW_SUMLEV }, safe=True)

    count_tested = 0
    count_allocated = 0
    count_new_features = 0

    for geography in collection.find({ 'sumlev': config.SUMLEV_BLOCK }):
        if points:
            lat = points[geography['geoid']]['lat']
            lon = points[geography['geoid']]['lon']
        else:
            lat = float(geography['metadata']['INTPTLAT'])
            lon = float(geography['metadata']['INTPTLON'])

        feature_id = find_geometry_containing_point(lat, lon)

        count_tested += 1

        if not feature_id:
            continue

        new_geoid = make_custom_geoid(NEW_SUMLEV, feature_id)
        new_geography = collection.find_one({ 'geoid': new_geoid })

        # Create an aggregating geography if it doesn't exist
        if not new_geography:
            new_geography = {
                'sumlev': NEW_SUMLEV,
                'geoid': new_geoid,
                'metadata': {
                    'NAME': str(feature_id),
                },
                'data': {
                    dataset: {},
                }
            }

            count_new_features += 1
            
        # Update new geography with values from constituent block
        for table in geography['data'][dataset]:
            if table not in new_geography['data'][dataset]:
                new_geography['data'][dataset][table] = {}

            for field, value in geography['data'][dataset][table].items():
                if field not in new_geography['data'][dataset][table]:
                    new_geography['data'][dataset][table][field] = 0

                new_geography['data'][dataset][table][field] = float(new_geography['data'][dataset][table][field]) + float(value)

        collection.save(new_geography, safe=True) 

        count_allocated += 1

    print 'Tested: %i' % count_tested
    print 'Allocated: %i' % count_allocated
    print 'New Features: %i' % count_new_features

# Run!
points_2000 = load_2000_block_points(BLOCKS_DBF)
aggregate_geographies(utils.get_geography2000_collection(), '2000', points=points_2000)
aggregate_geographies(utils.get_geography_collection(), '2010')

