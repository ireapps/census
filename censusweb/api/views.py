import simplejson

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

import csv
import constants
import help_text
import mongoutils

def homepage(request):
    return render_to_response('homepage.html', {
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

def data_as_json(request, geoids):
    geographies = {}

    for geoid in geoids.split(','):
        g = mongoutils.get_geography(geoid)
        del g['_id']
        del g['xrefs']
        geographies[geoid] = g
        
    return HttpResponse(simplejson.dumps(geographies), mimetype='application/json')

DATA_ALTERNATIVES = ['2000','2010','delta','pct_change']

def csv_row_header(tables=None):
    if not tables:
        tables_list = mongoutils.get_tables_for_year("2010")
    else:
        tables_list = tables

    row = ["sumlev", "geoid", "name"]
    for table in tables_list:
        labels = mongoutils.get_labels_for_table("2010", table)
        for statistic in sorted(labels['labels']):
            for alternative in DATA_ALTERNATIVES:
                if alternative == '2010':
                    row.append(statistic)
                else:
                    row.append("%s.%s" % (statistic,alternative))

    return row
    
def csv_row_for_geography(geography, tables=None):
    if not tables:
        tables_list = mongoutils.get_tables_for_year("2010")
    else:
        tables_list = tables

    row = [
        geography['sumlev'],
        geography['geoid'],
        geography['metadata']['NAME']
    ]
    for table in tables_list:
        labels = mongoutils.get_labels_for_table("2010", table)
        for statistic in sorted(labels['labels']):
            for alternative in DATA_ALTERNATIVES:
                try:
                    row.append( geography['data'][alternative][table][statistic] )
                except KeyError:
                    row.append('')

    return row

def data_as_csv(request, geoids):
    tables = request.GET.get("tables", None)
    if tables:
        tables = tables.split(",")

    response = HttpResponse(mimetype="text/csv")
    w = csv.writer(response)
    w.writerow(csv_row_header(tables))

    for geoid in geoids.split(','):
        g = mongoutils.get_geography(geoid)
        csvrow = csv_row_for_geography(g, tables)
        w.writerow(csvrow)
    
    return response

def labels_as_json(request,year,tables=None):
    labels = {}
    if tables is None:
        tables = mongoutils.get_tables_for_year(year)
    else:    
        tables = tables.split(',')

    for t in tables:
        l = mongoutils.get_labels_for_table(year,t)
        del l['_id']
        labels[t] = l
        
    return HttpResponse(simplejson.dumps(labels), mimetype='application/json')

def redirect_to_family(request, geoid):
    geography = mongoutils.get_geography(geoid)
    
    family = [geography['metadata']['STATE'],]
    if geography['metadata']['COUNTY']:
        family.append(
            "".join([geography['metadata']['STATE'], geography['metadata']['COUNTY']])
        )
    if geography['metadata']['PLACE']:
        family.append(
            "".join([geography['metadata']['STATE'], geography['metadata']['PLACE']])
        )
    if geography['metadata']['TRACT']:
        family.append(
            "".join([geography['metadata']['STATE'], geography['metadata']['COUNTY'], geography['metadata']['TRACT']])
        )
    
    geoid_str = ",".join(family)
    url = reverse("data", args=[geoid_str,])
    return HttpResponsePermanentRedirect(url)

def data(request, geoids):
    geographies = []

    for geoid in geoids.split(','):
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
            'universe': labels['universe'],
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
            
            report['rows'].append((label, data, key))

        for g in geographies:
            column_meta = {}
            column_name = g['metadata']['NAME']

            if g['sumlev'] in [constants.SUMLEV_COUNTY, constants.SUMLEV_PLACE, constants.SUMLEV_TRACT]:
                column_name += ', %s' % constants.FIPS_CODES_TO_STATE[g['metadata']['STATE']]

            column_meta['name'] = column_name
            column_meta['geoid'] = g['geoid']
            column_meta['sumlev'] = g['sumlev']
            report['columns'].append(column_meta)

        reports.append(report)

    return render_to_response('data.html',
        {
            'constants': constants,
            'reports': reports,
            'csv_url': request.get_full_path().replace('.html','.csv'),
            'json_url': request.get_full_path().replace('.html','.json'),
            'show_remove_button': len(report['columns']) > 1,
        },
        context_instance=RequestContext(request))
