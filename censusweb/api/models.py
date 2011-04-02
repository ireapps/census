from django.db import models
from django.db import connection

# Create your models here.

# def zero_pad(s,length):
#     if len(s) >

def state_fips_for_alpha(state_code):
    """
    Dependent upon load_fips management command.
    """
    cursor = connection.cursor()
    cursor.execute("SELECT distinct state_fips from county_lookup where state_code = %s",[state_code])
    row = cursor.fetchone()
    return row[0]

def clean_state(state):
    if not state.isdigit():
        state = state_fips_for_alpha(state)
    return state

def data_for_tract(state,county,tract):
    state = clean_state(state)
    cursor = connection.cursor()
    cols = ['SELECT * from tract_data where state_fips = %s']
    args = [state]
    if county:
        cols.append('county_fips = %s')
        args.append(county)
    if tract:
        cols.append('tract = %s')
        args.append(tract)

    statement = ' and '.join(cols)
    print "sql: ", statement
    print
    print "args: ", args
    cursor.execute(statement, args)
    results = []
    for row in cursor.fetchall():
        results.append(dict((desc[0], value) for desc, value in zip(cursor.description, row)))
    return results

def get_counties_by_state(state):
    return get_rows('SELECT county_name, county_fips, state_fips from county_lookup where state_code = %s order by county_name asc', [state])

def get_places_by_state(state):
    return get_rows('SELECT place_name, geo_id from place_lookup where state_code = %s order by place_name asc', [state])

def get_subdivisions_by_county(fips):
    return get_rows('SELECT county_subdivision_name, geo_id from county_subdivision_lookup where  = %s order by county_subdivision_name asc', [])

def get_rows(query, data):
    results = []
    cursor = connection.cursor()
    cursor.execute(query, data)
    for row in cursor.fetchall():
        results.append(row)
    return results
