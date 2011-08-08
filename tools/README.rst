census.ire.org tools
====================
As an adjunct to the core census.ire.org web app, we are collecting scripts and other useful resources for the community of census data users. If you'd like to contribute something you've made, send us a pull request, or send an email to Joe Germuska <jgermuska@tribune.com>

SQL
===
The SQL directory contains create table scripts for working with SF1 data, and a general script for Census 2010 geoheaders. These are meant to be used to directly load the raw data files, with all columns.

For the geoheader files, which are fixed width, you may find useful the csvkit library, which has a tool called 'in2csv' which can be used to convert fixed-width files to CSV.

* Install CSVKit using "easy_install csvkit" or from https://github.com/onyxfish/csvkit
* execute a command like this, taking care to use the correct paths and adjust for the specific geoheader file you are adapting:
    in2csv -e latin1 -s census2010_geo_schema.csv higeo2010.sf1> higeo2010.csv

NOTE: Take care with character encoding. Some place names (such as those with Spanish words) contain non-ASCII characters. The Census Bureau encodes the files using "latin-1" encoding.
The in2csv example above handles this correctly. in2csv always writes output files in UTF-8, so adjust your database load scripts accordingly.

Thanks to Ron Campbell of the Orange County Register for contributing the basis of **geo_2010.sql** Thanks to Mike Stucka of the Telegraph of Macon for suggestions to clarify the SQL and make it more compatible.

Note that the column IDs do not exactly match the values printed in the SF1 technical documentation. Our method was to zero-pad digits to three positions, but we made no allowance for the occasional presence of letters qualifying race/ethnic variations on certain tables. Therefore, our column lengths vary in length somewhat compared to the SF1 versions of the labels. (If anyone is motivated to create an alternate SQL file or view which maintains tighter consistency with the SF1 technical documentation, please feel free to send a file or issue a pull request.)

The column names in our SQL files align with the metadata files described below.

SAS
===
Dan Keating of the Washington Post has contributed a SAS script for loading the SF1 tables into a SAS environment. Note that data field labels in this script adhere to a pattern different than those used for the SQL scripts and in the metadata.

Metadata
========
These files provide machine-readable distillations of table and field codes and names. The label codes should match with column codes in the SQL script above.

All files in this directory are UTF-8 encoded.