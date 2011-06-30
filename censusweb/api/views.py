import simplejson

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound

from django.shortcuts import render_to_response
from django.contrib.gis.shortcuts import render_to_kml, render_to_kmz
from django.template import RequestContext, Template, Context

from boundaryservice.models import Boundary

import csv
import help_text
import mongoutils
import utils
from datetime import datetime

DATA_ALTERNATIVES = ['2000', '2010', 'delta', 'pct_change']

def homepage(request):
    return render_to_response('homepage.html', {
            'help_text': help_text,
            'settings': settings,
        },
        context_instance=RequestContext(request))
    
def generic_view(request, template=None, **kwargs):
    return render_to_response(template, { 'settings': settings }, context_instance=RequestContext(request))


def download_data_for_region(request, sumlev='', containerlev='', container='', datatype=''):
    print sumlev, containerlev
    if sumlev == '140' and containerlev == '040':
        geo_list = utils.fetch_tracts_by_state(container)
    elif sumlev == '140' and containerlev == '050':
        geo_list = utils.fetch_tracts_by_county(container)
    elif sumlev == '060' and containerlev == '050':
        geo_list = utils.fetch_county_subdivisions_by_county(container)
    elif sumlev == '160' and containerlev == '040':
        geo_list = utils.fetch_places_by_state(container)
    elif sumlev == '050' and containerlev == '040':
        geo_list = utils.fetch_counties_by_state(container)
    elif sumlev == '060' and containerlev == '040':
        geo_list = utils.fetch_county_subdivisions_by_state(container)

    geoids = ','.join([g[1] for g in geo_list])

    if datatype == 'csv':
        return data_as_csv(request, geoids)
    elif datatype == 'json':
        return data_as_json(request, geoids)

def get_tables_for_request(request):
    tables = request.GET.get("tables", None)

    if tables:
        tables = tables.split(",")
    else:
        tables = settings.DEFAULT_TABLES 

    return tables

# --- JSON ---
def data_as_json(request, geoids):
    tables = get_tables_for_request(request) 

    geographies = {}

    geoids_list = filter(lambda g: bool(g), geoids.split(','))

    for g in utils.fetch_geographies(geoids_list):
        del g['xrefs']

        for table in g["data"]["2010"].keys():
            if table not in tables:
                del g["data"]["2010"][table]

                # Not all data has 2000 values
                try:
                    del g["data"]["2000"][table]
                    del g["data"]["delta"][table]
                    del g["data"]["pct_change"][table]
                except KeyError:
                    continue

        geographies[g['geoid']] = g
        
    return HttpResponse(simplejson.dumps(geographies), mimetype='application/json')

# --- CSV ---
def data_as_csv(request, geoids):
    tables = get_tables_for_request(request) 
    labelset = mongoutils.get_labelset()

    response = HttpResponse(mimetype="text/csv")
    w = csv.writer(response)
    w.writerow(_csv_row_header(tables, labelset))

    geoids_list = filter(lambda g: bool(g), geoids.split(','))

    for g in utils.fetch_geographies(geoids_list):
        csvrow = _csv_row_for_geography(g, tables, labelset)
        w.writerow(csvrow)

    now = datetime.now()
    date_string = "%s-%s-%s-%s" % (now.year, now.month, now.day, now.microsecond)
    response['Content-Disposition'] = "attachment; filename=ire-census-%s.csv" % date_string

    return response

def _csv_row_header(tables, labelset):
    row = ["sumlev", "geoid", "name"]

    for table in tables:
        # Fail gracefully if a table isn't loaded (as in test
        try:
            labels = labelset['tables'][table]['labels']
        except KeyError:
            continue

        for statistic in sorted(labels.keys()):
            for alternative in DATA_ALTERNATIVES:
                if alternative == '2010':
                    row.append(statistic)
                else:
                    row.append("%s.%s" % (statistic,alternative))

    return row
    
def _csv_row_for_geography(geography, tables, labelset):
    row = [
        geography['sumlev'],
        geography['geoid'],
        geography['metadata']['NAME']
    ]

    for table in tables:
        # Fail gracefully if a table isn't loaded (as in test
        try:
            labels = labelset['tables'][table]['labels']
        except KeyError:
            continue

        for statistic in sorted(labels.keys()):
            for alternative in DATA_ALTERNATIVES:
                try:
                    row.append( geography['data'][alternative][table][statistic] )
                except KeyError:
                    row.append('')

    return row

# --- KML ---
def data_as_kml(request, geoids, format='kml'):
    tables = get_tables_for_request(request) 

    geoid_list = filter(lambda g: bool(g), geoids.split(','))
    boundaries = dict((b.external_id, b) for b in Boundary.objects.filter(external_id__in=geoid_list))
    json_data = dict((j['geoid'], j) for j in utils.fetch_geographies(geoid_list))
    labelset = mongoutils.get_labelset()
    
    placemarks = [
        _create_placemark_dict(boundaries[geoid], json_data[geoid], tables, labelset) for geoid in geoid_list
    ] 

    if format == 'kmz':
        render = render_to_kmz
    else:
        render = render_to_kml

    return render('gis/kml/placemarks.kml', {'places' : placemarks})            

def _create_placemark_dict(b, j, tables, labelset):
    """
    Each placemark should have a name, a description, and kml which includes <ExtraData>
    """
    p = {
       'name': b.display_name,
       'description': 'Summary Level: %(sumlev)s; GeoID: %(geoid)s' % (j),
    }

    kml_context = _build_kml_context_for_template(b, j, tables, labelset)
    shape = b.simple_shape.transform(4326, clone=True)
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

def _build_kml_context_for_template(b, j, tables, labelset):
    kml_context = { 'data': [] }

    for table in tables:
        # Fail gracefully if a table isn't loaded (as in test
        try:
            labels = labelset['tables'][table]['labels']
        except KeyError:
            continue

        for statistic in sorted(labels.keys()):
            for alternative in DATA_ALTERNATIVES:
                #print "t: %s, a: %s, s: %s" % (table, alternative, statistic)
                try: 
                    datum = {
                        'value': j['data'][alternative][table][statistic]
                    }

                    if alternative == '2010':
                        datum['name'] = statistic
                    else:
                        datum['name'] = "%s.%s" % (statistic, alternative)

                    datum['display_name'] = labels[statistic]['text']
                    kml_context['data'].append(datum)

                except KeyError:
                    pass

    return kml_context
    
def generate_sql(request, file_ids=None, table_ids=None, aggregate=None):
    if aggregate == 'all_files':
        sql = utils.generate_create_sql_by_file()
        return HttpResponse(sql,mimetype='text/plain')
    elif aggregate == 'all_tables':
        sql = utils.generate_sql_by_table()
        return HttpResponse(sql,mimetype='text/plain')
    elif aggregate == 'all_table_views':
        sql = utils.generate_views_by_table()
        return HttpResponse(sql,mimetype='text/plain')
    elif aggregate is not None:
        return HttpResponseNotFound()

    if file_ids:
        ids = map(int,file_ids.split(','))
        sql = utils.generate_create_sql_by_file(file_numbers=ids)
        return HttpResponse(sql,mimetype='text/plain')

    if table_ids:    
        table_ids = table_ids.split(',')
        sql = utils.generate_sql_by_table(table_ids)
        return HttpResponse(sql,mimetype='text/plain')

    return HttpResponseNotFound()

