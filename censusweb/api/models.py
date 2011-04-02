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
    state_fips  = fips[0:2]
    county_fips = fips[2:]
    return get_rows('SELECT county_subdivision_name, geo_id from county_subdivision_lookup where state_fips = %s and county_fips = %s order by county_subdivision_name asc', [state_fips, county_fips])

def get_tracts_by_county(fips):
    state_fips  = fips[0:2]
    county_fips = fips[2:]
    return get_rows('SELECT name, tract from tract_data where state_fips = %s and county_fips = %s order by name asc', [state_fips, county_fips])

def get_rows(query, data):
    results = []
    cursor = connection.cursor()
    cursor.execute(query, data)
    for row in cursor.fetchall():
        results.append(row)
    return results
    
def get_state_name(state_code):
    states = {
        'AK': 'Alaska',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'AL': 'Alabama',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MH': 'Marshall Islands',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
    }
    return states[state_code]

def get_county_name(county_fips):
    cursor = connection.cursor()
    cursor.execute("SELECT county_name from county_lookup where county_fips = %s",[county_fips])
    row = cursor.fetchone()
    return row[0]

