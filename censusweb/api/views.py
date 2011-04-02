from django.http import HttpResponseRedirect, HttpResponse
from django.core import serializers
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

import simplejson
import csv
import re

from models import data_for_tract, get_counties_by_state, get_places_by_state, get_subdivisions_by_county, get_tracts_by_county
from statmodels import AgeSex, Report

def tracts(request, extension, state="", county="", tract=""):

    data = data_for_tract(state,county,tract)
    agesex = AgeSex(census2000=data[0])
    report = Report()
    report.add(agesex)

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
                'report': report,
            },
            context_instance=RequestContext(request))

def stats(request,group):
    response = HttpResponse(mimetype='text/plain')
    response.write("You asked for %s" % group)
    data = data_for_tract('01','001','020100')
    from statmodels import AgeSex
    agesex = AgeSex(census2000=data[0])
    response.write("\nTotal 2000: %i" % agesex.total_population.census2000)
    response.write("\nTotal 2010: %i" % agesex.total_population.census2010)
    return response

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

def tracts_for_county(request, county=""):
    tracts = get_tracts_by_county(county)
    return HttpResponse(simplejson.dumps(tracts), mimetype='application/json')
