"""
"""
from django.core.management.base import BaseCommand, CommandError, handle_default_options
from optparse import make_option

import csv
from urllib import urlopen
from django.db import connection
from django.db import connection, transaction
    
class Command(BaseCommand):
    args=''
    help=''
    option_list= BaseCommand.option_list + ()

    def get_version(self):
        return "0.1"

    def handle(self, *args, **options):
        """
        Create a lookup table based on data.
        explanation: http://www.census.gov/geo/www/ansi/download.html
        """
        cur = connection.cursor()
        cur.execute("drop table if exists county_lookup")
        # State,State ANSI,County ANSI,County Name,ANSI Cl
        cur.execute("""
            create table county_lookup (
                state_code char(2),
                state_fips char(2),
                county_fips char(3),
                county_name varchar(255),
                ansi_class char(2)
            )
        """)
        
        reader = csv.reader(urlopen("http://www.census.gov/geo/www/ansi/national.txt"))
        headers = reader.next() # junk
        INSERT = "insert into county_lookup (state_code, state_fips, county_fips, county_name, ansi_class) values (%s,%s,%s,%s,%s)"
        for row in reader:
            cur.execute(INSERT,row)

        transaction.commit_unless_managed()

        