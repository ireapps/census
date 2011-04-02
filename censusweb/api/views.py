from django.http import HttpResponseRedirect, HttpResponse
from django.core import serializers
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

import simplejson
import csv

from models import data_for_tract, get_counties_by_state
# Create your views here.

def tracts(request, extension, state="", county="", tract=""):

    data = data_for_tract(state,county,tract)

    if extension == 'json':
        return HttpResponse(simplejson.dumps(data), mimetype='application/json')

    elif extension == 'csv':
        response = HttpResponse(mimetype='text/csv')
        filename = "%s%s%s.csv" % (state,county,tract)
        response['Content-Disposition'] = 'attachment; filename=' + filename
        writer = csv.writer(response)
        writer.writerow(data.values())
        return response

    else: #html
        return render_to_response('tracts.html',
            {
                'state': state,
                'county': county,
                'tract': tract,
                'extension': extension,
                'data': data,
            },
            context_instance=RequestContext(request))

def stat_group_config(group):
    import csv
    import os.path
    from django.conf import settings
    path = os.path.join(settings.SITE_ROOT,'config/statgroups','%s.csv' % group)
    print path
    return list(csv.reader(open(path)))
    
def stats(request,group):
    state, county, tract = ['MS','001','000100']
    data = data_for_tract(state, county, tract)
    conf = stat_group_config(group)
    
    response = HttpResponse(mimetype='text/plain')
    response.write("There are %i rows of data\n\n" % len(data))
    w = csv.writer(response)
    output_rows = []
    for i,conf_row in enumerate(conf):
        stat = conf_row[-1]
        row = conf_row[:-1]
        if i == 0:
            header = [''] * len(row)
        for data_row in data:
            row.append(data_row[stat.lower()])
            if i == 0: header.append(stat.lower())
        if i == 0: output_rows.append(header)
        output_rows.append(row)
    
    w.writerows(output_rows)
    return response
    
def homepage(request):
    return render_to_response('homepage.html', context_instance=RequestContext(request))

def counties_for_state(request, state=""):
    counties = get_counties_by_state(state)
    return HttpResponse(simplejson.dumps(counties), mimetype='application/json')
