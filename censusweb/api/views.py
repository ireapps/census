import simplejson

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response
from django.contrib.gis.shortcuts import render_to_kml, render_to_kmz
from django.template import RequestContext, Template, Context

from boundaryservice.models import Boundary

import csv
import constants
import help_text
import mongoutils
from datetime import datetime

DATA_ALTERNATIVES = ['2000','2010','delta','pct_change']

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
    
def tracts_for_state(request, state=''):
    tracts = mongoutils.get_tracts_by_state(state)
    return HttpResponse(simplejson.dumps(tracts), mimetype='application/json')
    
def download_data_for_region(request, sumlev='', containerlev='', container='', datatype=''):
    if sumlev == '140' and containerlev == '040':
        geo_list = mongoutils.get_tracts_by_state(container)
    elif sumlev == '140' and containerlev == '050':
        geo_list = mongoutils.get_tracts_by_county(container)
    elif sumlev == '160' and containerlev == '040':
        geo_list = mongoutils.get_places_by_state(container)
    elif sumlev == '050' and containerlev == '040':
        geo_list = mongoutils.get_counties_by_state(container)

    geoids = ','.join([g[1] for g in geo_list])

    if datatype == 'csv':
        return data_as_csv(request,geoids)
    elif datatype == 'json':
        return data_as_json(request,geoids)

def data_as_json(request, geoids):
    geoid_list = filter(lambda g: bool(g), geoids.split(','))
    geographies = {}

    for g in mongoutils.get_geographies_list(geoid_list):
        del g['_id']
        del g['xrefs']
        geographies[g['geoid']] = g

    return HttpResponse(simplejson.dumps(geographies), mimetype='application/json')

def family_as_json(request, geoid):
    geographies = {}
    
    family_geoids = get_family_geoids(geoid)
    for g in mongoutils.get_geographies_list(family_geoids, ['geoid', 'sumlev', 'metadata.NAME', 'metadata.STATE', 'metadata.COUNTY']):
        del g['_id']
        #del g['xrefs']
        geographies[g['geoid']] = g
        
    return HttpResponse(simplejson.dumps(geographies), mimetype='application/json')

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

    geoids_list = filter(lambda g: bool(g), geoids.split(','))
    for g in mongoutils.get_geographies_list(geoids_list):
        csvrow = csv_row_for_geography(g, tables)
        w.writerow(csvrow)

    now = datetime.now()
    date_string = "%s-%s-%s-%s" % (now.year, now.month, now.day, now.microsecond)
    response['Content-Disposition'] = "attachment; filename=ire-census-%s.csv" % date_string

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
    family = get_family_geoids(geoid)
    geoid_str = ",".join(family)
    url = reverse("data", args=[geoid_str,])
    return HttpResponsePermanentRedirect(url)

def get_family_geoids(geoid):
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
    return family

def report_values_for_key(g,t,key):
    d = {}
    for alternative in DATA_ALTERNATIVES:
        try:
            d[alternative] = g['data'][alternative][t][key]
        except KeyError:
            d[alternative] = ''
    return d

def report_for_table(geographies, year, t):
    labels = mongoutils.get_labels_for_table(year, t)

    report = {
        'key': t,
        'name': labels['name'],
        'year': year,
        'table': t + ". " + labels['name'],
        'universe': labels['universe'],
        'columns': [],
        'rows': [],
    }

    for key, label in sorted(labels['labels'].items()):
        data = []

        for g in geographies:
            data.append(report_values_for_key(g,t,key))

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

    return report
    
def data(request, geoids):
    geoids_list = filter(lambda g: bool(g), geoids.split(','))
    geographies = mongoutils.get_geographies_list(geoids_list)

    tables = []
    
    for g in geographies:
        tables.extend(g['data']['2010'].keys())

    tables = set(tables)

    reports = []

    for t in sorted(tables):
        report = report_for_table(geographies, '2010',t)
        reports.append(report)

    return render_to_response('data.html',
        {
            'constants': constants,
            'reports': reports,
            'csv_url': request.get_full_path().replace('.html','.csv'),
            'json_url': request.get_full_path().replace('.html','.json'),
            'show_remove_button': len(geoids_list) > 1,
            'last_geoid': g['geoid'],
            'geoids': geoids_list
        },
        context_instance=RequestContext(request))

# --- KML BEGIN ---
def data_as_kml(request, geoids,format='kml'):
    geoid_list = filter(lambda g: bool(g), geoids.split(','))
    boundaries = dict((b.external_id,b) for b in Boundary.objects.filter(external_id__in=geoid_list))
    json_data = dict((j['geoid'],j) for j in mongoutils.get_geographies_list(geoid_list))
    
    placemarks = [
        _create_placemark_dict(boundaries[geoid],json_data[geoid]) for geoid in geoid_list
    ] 

    if format == 'kmz':
        render = render_to_kmz
    else:
        render = render_to_kml
    return render('gis/kml/placemarks.kml', {'places' : placemarks})            

def _create_placemark_dict(b,j,tables=None):
    """each thing should have a name, a description, and kml which includes <ExtraData>"""
    p = {
       'name': b.display_name,
       'description': 'Summary Level: %(sumlev)s; GeoID: %(geoid)s' % (j),
    }

    if not tables:
        tables_list = mongoutils.get_tables_for_year("2010")
    else:
        tables_list = tables

    kml_context = _build_kml_context_for_template(b,j,tables_list)
    shape = b.simple_shape.transform(4326,clone=True)
    p['kml'] = shape.kml + KML_EXTENDED_DATA_TEMPLATE.render(Context(kml_context))
    
    return p

KML_EXTENDED_DATA_TEMPLATE = Template("""
<ExtendedData>
    {% for datum in data %}
  <Data name="{{datum.name}}">{% if datum.display_name %}
    <displayName><![CDATA[{{datum.display_name}}]]></displayName>{% endif %}
    <value><![CDATA[{{datum.value}}]]></value>
  </Data>
  {% endfor %}
</ExtendedData>""")

def _build_kml_context_for_template(b,j,tables_list):
    kml_context = { 'data': [] }
    for table in tables_list:
        labels = mongoutils.get_labels_for_table("2010", table)
        for statistic in sorted(labels['labels']):
            for alternative in DATA_ALTERNATIVES:
                print "t: %s, a: %s, s: %s" % (table, alternative, statistic)
                try: 
                    datum = { 'value': j['data'][alternative][table][statistic] }
                    if alternative == '2010':
                        datum['name'] = statistic
                    else:
                        datum['name'] = "%s.%s" % (statistic,alternative)
                    datum['display_name'] = labels['labels'][statistic]['text']
                    kml_context['data'].append(datum)
                except KeyError: pass
    return kml_context
    
# --- KML END ---
