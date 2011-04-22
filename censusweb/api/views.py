from django.http import HttpResponseRedirect, HttpResponse
from django.core import serializers
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

import simplejson
import csv
import re

import help_text
from models import data_for_tract, get_counties_by_state, get_places_by_state, get_subdivisions_by_county, get_tracts_by_county, get_state_name, get_county_name
from statmodels import AgeSex, Report

def data(request, slugs, extension):

    summaries = []
    filename = ""
    for slug in slugs.split("/"):
        summarylevel,state,county,tract = slug.split("-")
        summaries.append({
             "summarylevel": summarylevel,
             "state": state,
             "county": county,
             "tract": tract,
             "slug": slug,
        })
        filename += "%s_" % slug
    filename = filename[:-1]

    reports = []
    for summary in summaries:
        data = data_for_tract(summary["state"],summary["county"],summary["tract"])
        agesex = AgeSex(census2000=data[0])
        report = Report(summary["slug"], summary["state"], summary["county"], summary["tract"])
        report.add(agesex)
        reports.append(report)

    if extension == 'json':
        json = []
        for report in reports:
            json.append(report.as_json())
        return HttpResponse(simplejson.dumps(json), mimetype='application/json')

    elif extension == 'csv':
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + filename
        writer = csv.writer(response)
        for report in reports:
            writer.writerows(report.as_csv())
        return response

    else: #html
        return render_to_response('data.html',
            {
                'extension': extension,
                'reports': reports,
                'csv_url': request.get_full_path().replace('.html','.csv'),
                'json_url': request.get_full_path().replace('.html','.json'),
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
    return render_to_response('homepage.html',
    {
        'help_text': help_text,
    },
    context_instance=RequestContext(request))

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
