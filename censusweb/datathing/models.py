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
    cursor.execute("select distinct state_fips from fips_lookup where state_code = %s",[state_code])
    row = cursor.fetchone()
    return row[0]

def clean_state(state):
    if not state.isdigit():
        state = state_fips_for_alpha(state)
    return state

def data_for_tract(state,county,tract):
    state = clean_state(state)
    cursor = connection.cursor()
    print [state, county, tract]
    cursor.execute("SELECT * from tract_data where state_fips = %s and county_fips = %s and tract = %s", [state, county, tract])
    row = cursor.fetchone()
    return dict((desc[0], value) for desc, value in zip(cursor.description, row))
