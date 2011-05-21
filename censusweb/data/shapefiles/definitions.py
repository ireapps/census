"""
Configuration describing the shapefiles to be loaded.
"""
from datetime import date

class simple_namer():
    """
    Name features with a joined combination of attributes, optionally passing the result through a normalizing function.
    """
    def __init__(self, attribute_names, seperator=' ', normalizer=None):
        self.attribute_names = attribute_names
        self.seperator = seperator
        self.normalizer = normalizer

    def __call__(self, feature):
        attribute_values = map(str, map(feature.get, self.attribute_names))
        name = self.seperator.join(attribute_values).strip()
    
        if self.normalizer:
            normed = self.normalizer(name)
            if not normed:
                raise ValueError('Failed to normalize \"%s\".' % name)
            else:
                name = normed

        return name

SHAPEFILES = {
    # This key should be the plural name of the boundaries in this set
    'States': {
        # Path to a shapefile, relative to /data
        'file': 'STATE/tl_2010_us_state10.zip',
        # Generic singular name for an boundary of from this set
        'singular': 'State',
        # Should the singular name come first when creating canonical identifiers for this set?
        # (e.g. True in this case would result in "Neighborhood South Austin" rather than "South Austin Neighborhood")
        'kind_first': False,
        # Function which each feature wall be passed to in order to extract its "external_id" property
        # The utils module contains several generic functions for doing this
        'ider': simple_namer(['GEOID10']),
        # Function which each feature will be passed to in order to extract its "name" property
        'namer': simple_namer(['NAME10']),
        # Authority that is responsible for the accuracy of this data
        'authority': 'U.S. Census Bureau, Geography Division',
        # Geographic extents which the boundary set encompasses
        'domain': 'United States',
        # Last time the source was checked for new data
        'last_updated': date(2011, 05, 21),
        # A url to the source of the data
        'href': 'http://www.census.gov/cgi-bin/geo/shapefiles2010/main',
        # Notes identifying any pecularities about the data, such as columns that were deleted or files which were merged
        'notes': '',
        # Encoding of the text fields in the shapefile, i.e. 'utf-8'. If this is left empty 'ascii' is assumed
        'encoding': 'latin-1'
        # SRID of the geometry data in the shapefile if it can not be inferred from an accompanying .prj file
        # This is normally not necessary and can be left undefined or set to an empty string to maintain the default behavior
        #'srid': ''
    },
    # This key should be the plural name of the boundaries in this set
    'Counties': {
        # Path to a shapefile, relative to /data
        'file': 'COUNTY/tl_2010_us_county10.zip',
        # Generic singular name for an boundary of from this set
        'singular': 'County',
        # Should the singular name come first when creating canonical identifiers for this set?
        # (e.g. True in this case would result in "Neighborhood South Austin" rather than "South Austin Neighborhood")
        'kind_first': False,
        # Function which each feature wall be passed to in order to extract its "external_id" property
        # The utils module contains several generic functions for doing this
        'ider': simple_namer(['GEOID10']),
        # Function which each feature will be passed to in order to extract its "name" property
        'namer': simple_namer(['NAME10']),
        # Authority that is responsible for the accuracy of this data
        'authority': 'U.S. Census Bureau, Geography Division',
        # Geographic extents which the boundary set encompasses
        'domain': 'United States',
        # Last time the source was checked for new data
        'last_updated': date(2011, 05, 21),
        # A url to the source of the data
        'href': 'http://www.census.gov/cgi-bin/geo/shapefiles2010/main',
        # Notes identifying any pecularities about the data, such as columns that were deleted or files which were merged
        'notes': '',
        # Encoding of the text fields in the shapefile, i.e. 'utf-8'. If this is left empty 'ascii' is assumed
        'encoding': 'latin-1'
        # SRID of the geometry data in the shapefile if it can not be inferred from an accompanying .prj file
        # This is normally not necessary and can be left undefined or set to an empty string to maintain the default behavior
        #'srid': ''
    },
}
