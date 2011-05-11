import simplejson

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

import constants
import help_text
import mongoutils

def homepage(request):
    return render_to_response('homepage.html',
    {
        'help_text': help_text,
    },
    context_instance=RequestContext(request))

def counties_for_state(request, state=''):
    counties = mongoutils.get_counties_by_state(state)
    return HttpResponse(simplejson.dumps(counties), mimetype='application/json')

def places_for_state(request, state=''):
    places = mongoutils.get_places_by_state(state)
    return HttpResponse(simplejson.dumps(places), mimetype='application/json')

def tracts_for_county(request, county=''):
    tracts = mongoutils.get_tracts_by_county(county)
    return HttpResponse(simplejson.dumps(tracts), mimetype='application/json')

def data(request, geoids, extension):
    geographies = []

    for geoid in geoids.split('/'):
        geographies.append(mongoutils.get_geography(geoid))

    tables = []
    
    for g in geographies:
        tables.extend(g['data']['2010'].keys())

    tables = set(tables)

    reports = []

    for t in sorted(tables):
        labels = mongoutils.get_labels_for_table('2010', t)

        report = {
            'year': '2010',
            'table': t + ". " + labels['name'],
            'columns': [],
            'rows': [],
        }

        for key, label in sorted(labels['labels'].items()):
            data = []

            for g in geographies:
                try:
                    data.append({
                        '2000': g['data']['2000'][t][key],
                        '2010': g['data']['2010'][t][key],
                        'delta': g['data']['delta'][t][key],
                        'pct_change': g['data']['pct_change'][t][key]
                    })
                # Data not available for 2000
                except KeyError:
                    data.append({
                        '2010': g['data']['2010'][t][key],
                    })
            
            report['rows'].append((label, data))

        for g in geographies:
            c = g['metadata']['NAME']

            if g['sumlev'] in [constants.SUMLEV_COUNTY, constants.SUMLEV_PLACE, constants.SUMLEV_TRACT]:
                c += ', %s' % constants.FIPS_CODES_TO_STATE[g['metadata']['STATE']]

            report['columns'].append(c)

        reports.append(report)

    return render_to_response('data.html',
        {
            'constants': constants,
            'reports': reports,
            'csv_url': request.get_full_path().replace('.html','.csv'),
            'json_url': request.get_full_path().replace('.html','.json'),
        },
        context_instance=RequestContext(request))
