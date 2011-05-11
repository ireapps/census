import simplejson
import csv

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

import help_text
import mongoutils

def data(request, slugs, extension):
    summaries = []
    filename = ""
    for slug in slugs.split("/"):
        summarylevel, state, county, tract = slug.split("-")
        summaries.append({
             "state": state,
             "county": county,
             "tract": tract,
        })
        filename += "%s_" % slug
    filename = filename[:-1]

    geographies = []

    for summary in summaries:
        geographies.extend(mongoutils.get_geographies(summary["state"], summary["county"], summary["tract"]))

    tables = []
    
    for g in geographies:
        tables.extend(g['data']['2010'].keys())

    tables = set(tables)

    reports = []

    for t in sorted(tables):
        labels = mongoutils.get_labels_for_table('2010', t)

        report = {
            'year': '2010',
            'table': t,
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
            report['columns'].append({
                'tract': g['metadata']['TRACT'],
                'county': g['metadata']['COUNTY'],
                'state': g['metadata']['STATE']
            })

        reports.append(report)

    return render_to_response('data.html',
        {
            'reports': reports,
            'csv_url': request.get_full_path().replace('.html','.csv'),
            'json_url': request.get_full_path().replace('.html','.json'),
        },
        context_instance=RequestContext(request))

def homepage(request):
    return render_to_response('homepage.html',
    {
        'help_text': help_text,
    },
    context_instance=RequestContext(request))

def counties_for_state(request, state=""):
    counties = mongoutils.get_counties_by_state(state)
    return HttpResponse(simplejson.dumps(counties), mimetype='application/json')

def places_for_state(request, state=""):
    places = mongoutils.get_places_by_state(state)
    return HttpResponse(simplejson.dumps(places), mimetype='application/json')

def tracts_for_county(request, county=""):
    tracts = mongoutils.get_tracts_by_county(county)
    return HttpResponse(simplejson.dumps(tracts), mimetype='application/json')
