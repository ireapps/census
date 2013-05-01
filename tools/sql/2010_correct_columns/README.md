This directory contains a Ruby script and generated .sql file for the SF1 segments/files/tables, with correct column names that match up to the Data Dictionary Reference Names in the SF1 technical documentation.  It also generates a rename_columns.sql file that can be used to fix tables created with the original names.

It uses/parses the 'packing list' file from the AK SF1 zip file.

The generated files were produced with this: `./generate_sql.rb`
