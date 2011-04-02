from django.http import HttpResponseRedirect, HttpResponse
from django.core import serializers
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

import simplejson
import csv

from models import data_for_tract, get_counties_by_state, get_places_by_state, get_subdivisions_by_county

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

def homepage(request):
    return render_to_response('homepage.html', context_instance=RequestContext(request))

def counties_for_state(request, state=""):
    counties = get_counties_by_state(state)
    return HttpResponse(simplejson.dumps(counties), mimetype='application/json')

def places_for_state(request, state=""):
    places = get_places_by_state(state)
    return HttpResponse(simplejson.dumps(places), mimetype='application/json')

def subdivisions_for_county(request, county=""):
    subdivisions = get_subdivisions_by_county(county)
    return HttpResponse(simplejson.dumps(subdivisions), mimetype='application/json')
