=============
Data Overview
=============

The census.ire.org site will contain data from Summary File 1 of the 2010 Decennial Census.
For full details about the data contained in these tables,
please refer to Chapter 6 of the `Technical Documentation`_ provided by the Census Bureau.

.. _Technical Documentation: http://www.census.gov/prod/cen2010/doc/sf1.pdf

The Census Bureau is releasing the Summary File 1 data on a rolling basis
beginning in mid June.
Data for a few states will be released each week
and added to the census.ire.org site until all data are available sometime in August.

Deltas
======

For many tables and fields we were able to calculate the amount of change between 2000 and 2010.
However, due to changes in the Census questionaire, not all fields have direct equivalents.

For instance: In 2000, questions about family households asked about "own" children in the household,
but in 2010, the questions were about "related" children, so the figures are not directly comparable.

Also, some questions had more responses available in 2010 than in 2000, or vice versa.

For example: The Housing Tenure table in 2000 includes number of housing units owned. But in 2010,
the table includes units owned with a mortgage or loan and units owned free and clear.

Because the responses were not separated in 2000, we can only provide a delta for the total number owned.

.. _geography-label:

Geographies
===========

The census.ire.org site will provide data at several key levels of geography:
census tract, place, county subdivision, county and state.

Tract
-----

Tracts are created by the Census Bureau to contain an average of 4,000 people.
Their boundaries may change between decennial censuses and vary in size from city blocks to entire counties, depending on population density

In order to compare 2000 tracts to 2010 tracts,
we've calculated how the population and housing units from 2000 boundaries
would be distributed in the new 2010 boundaries using formulas provided by the Census Bureau.

U.S. Census: `Tract definition`_

.. _Tract definition: http://www.census.gov/geo/www/geo_defn.html#CensusTract


Place
-----

Places in Census Parlance include incorporated places legally established under state law;
consolidated cities, where functions of local and county governments have merged;
and Census Designated Places, areas of significant population with a well-known name, but not legally incorporated.

U.S. Census: `Place definition`_

.. _Place definition: http://www.census.gov/geo/www/geo_defn.html#Place


County Subdivision
------------------

In some states, townships are considered County Subdivisions, not "places."

U.S. Census: `County Subdivision definition`_

.. _County Subdivision definition: http://www.census.gov/geo/www/geo_defn.html#CountySubdivision


County and county equivalents
-----------------------------

Counties are the primary division of most states.
In Alaska, county-equivalent areas are known as "boroughs,"
and in Louisiana they are known as "parishes."

U.S. Census: `County definition`_

.. _County definition: http://www.census.gov/geo/www/geo_defn.html#County



Formats
=======

CSV
---

These are comma-separated-value files. They are plain-text files that can be opened in Excel or other programs for further analysis of the data.

CSV files will be transposed from the format seen on the web site.


KML
---

File suitable for using with Google Fusion Table's mapping feature or other spatial analysis tools.

JSON
----

Javascript Object Notation for use with web applications.

