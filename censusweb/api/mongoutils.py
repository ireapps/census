from django.conf import settings
from pymongo import Connection, ASCENDING

SUMLEV_NATION = '010'
SUMLEV_STATE = '040'
SUMLEV_COUNTY = '050'
SUMLEV_TRACT = '140'
SUMLEV_PLACE = '160'

FIPS_CODES = {
    'AK': '02',
    'AR': '05',
    'AS': '60',
    'AZ': '04',
    'AL': '01',
    'CA': '06',
    'CO': '08',
    'CT': '09',
    'DC': '11',
    'DE': '10',
    'FL': '12',
    'GA': '13',
    'HI': '15',
    'IA': '19',
    'ID': '16',
    'IL': '17',
    'IN': '18',
    'KS': '20',
    'KY': '21',
    'LA': '22',
    'MA': '25',
    'MD': '24',
    'ME': '23',
    'MH': '68',
    'MI': '26',
    'MN': '27',
    'MO': '29',
    'MS': '26',
    'MT': '29',
    'NC': '37',
    'ND': '38',
    'NE': '31',
    'NH': '33',
    'NJ': '34',
    'NM': '35',
    'NV': '32',
    'NY': '36',
    'OH': '39',
    'OK': '40',
    'OR': '41',
    'PA': '42',
    'PR': '72',
    'RI': '44',
    'SC': '45',
    'SD': '46',
    'TN': '47',
    'TX': '48',
    'UT': '49',
    'VA': '78',
    'VT': '50',
    'WA': '53',
    'WI': '55',
    'WV': '54',
    'WY': '56'
}        

def get_geographies():
    connection = Connection()
    db = connection[settings.CENSUS_DB] 
    return db[settings.GEOGRAPHIES_COLLECTION]

def state_fips_for_alpha(state_code):
    # TODO
    cursor = connection.cursor()
    cursor.execute("SELECT distinct state_fips from county_lookup where state_code = %s",[state_code])
    row = cursor.fetchone()
    return row[0]
    
def clean_state(state):
    # TODO
    if not state.isdigit():
        state = state_fips_for_alpha(state)
    return state

def data_for_tract(state, county, tract):
    #geographies = get_geographies()

    #geographies.find({ 'metadata.state':  

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
    geographies = get_geographies()

    counties = geographies.find({ 'metadata.STATE': FIPS_CODES[state], 'sumlev': SUMLEV_COUNTY }, fields=['metadata.STATE', 'metadata.COUNTY', 'metadata.NAME'], sort=[('metadata.NAME', ASCENDING)])

    return [(c['metadata']['NAME'], c['metadata']['COUNTY'], c['metadata']['STATE']) for c in counties] 

def get_places_by_state(state):
    return get_rows('SELECT place_name, geo_id from place_lookup where state_code = %s order by place_name asc', [state])

def get_subdivisions_by_county(fips):
    state_fips  = fips[0:2]
    county_fips = fips[2:]

    return get_rows('SELECT county_subdivision_name, geo_id from county_subdivision_lookup where state_fips = %s and county_fips = %s order by county_subdivision_name asc', [state_fips, county_fips])

def get_tracts_by_county(fips):
    state_fips  = fips[0:2]
    county_fips = fips[2:]

    geographies = get_geographies()

    tracts = geographies.find({ 'metadata.STATE': state_fips, 'metadata.COUNTY': county_fips, 'sumlev': SUMLEV_TRACT }, fields=['metadata.NAME', 'metadata.TRACT'], sort=[('metadata.NAME', ASCENDING)])

    return [(t['metadata']['NAME'], t['metadata']['TRACT']) for t in tracts] 

    #return get_rows('SELECT name, tract from tract_data where state_fips = %s and county_fips = %s order by name asc', [state_fips, county_fips])

def get_rows(query, data):
    results = []
    cursor = connection.cursor()
    cursor.execute(query, data)
    for row in cursor.fetchall():
        results.append(row)
    return results
    
def get_county_name(county_fips):
    cursor = connection.cursor()
    cursor.execute("SELECT county_name from county_lookup where county_fips = %s",[county_fips])
    row = cursor.fetchone()
    return row[0]

