census.ire.org tools
====================
As an adjunct to the core census.ire.org web app, we are collecting scripts and other useful 
resources for the community of census data users. If you'd like to contribute something
you've made, send us a pull request, or send an email to Joe Germuska <jgermuska@tribune.com>

SQL
===
The SQL directory contains create table scripts for working with SF1 data, and a general script
for Census 2010 geoheaders. These are meant to be used to directly load the raw data files, with 
all columns.  

For the geoheader files, which are fixed width, you may find useful the csvkit library, which has a
tool called 'in2csv' which can be used to convert fixed-width files to CSV.

* Install CSVKit using "easy_install csvkit" or from https://github.com/onyxfish/csvkit
* execute a command like this, taking care to use the correct paths and adjust for the specific geoheader file you are adapting:
    in2csv -s census2010_geo_schema.csv higeo2010.sf1> higeo2010.csv

Thanks to Ron Campbell of the Orange County Register for contributing the basis of the **geo_2010.sql**

SAS
===
Dan Keating of the Washington Post has contributed a SAS script for loading the SF1 tables into 
a SAS environment.

