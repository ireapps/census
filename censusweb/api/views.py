import simplejson

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.gis.shortcuts import render_to_kml, render_to_kmz
from django.template import RequestContext, Template, Context

from boundaryservice.models import Boundary

import csv
import help_text
import mongoutils # TODO: factor out
import utils
from datetime import datetime

DATA_ALTERNATIVES = ['2000','2010','delta','pct_change']

def homepage(request):
    return render_to_response('homepage.html', {
            'help_text': help_text,
            'settings': settings,
        },
        context_instance=RequestContext(request))
    
def data(request, geoids):
    return render_to_response('data.html', { 'settings': settings }, context_instance=RequestContext(request))

def download_data_for_region(request, sumlev='', containerlev='', container='', datatype=''):
    # TODO - reimplement
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
    geographies = {}

    geoids_list = filter(lambda g: bool(g), geoids.split(','))
    for g in utils.fetch_geographies(geoids_list):
        del g['xrefs']
        geographies[g['geoid']] = g
        
    return HttpResponse(simplejson.dumps(geographies), mimetype='application/json')

def _csv_row_header(tables=None):
    if not tables:
        tables_list = mongoutils.get_tables()
    else:
        tables_list = tables

    row = ["sumlev", "geoid", "name"]
    for table in tables_list:
        labels = mongoutils.get_labels_for_table(table)
        for statistic in sorted(labels['labels']):
            for alternative in DATA_ALTERNATIVES:
                if alternative == '2010':
                    row.append(statistic)
                else:
                    row.append("%s.%s" % (statistic,alternative))

    return row
    
def _csv_row_for_geography(geography, tables=None):
    if not tables:
        tables_list = mongoutils.get_tables()
    else:
        tables_list = tables

    row = [
        geography['sumlev'],
        geography['geoid'],
        geography['metadata']['NAME']
    ]
    for table in tables_list:
        labels = mongoutils.get_labels_for_table(table)
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
    w.writerow(_csv_row_header(tables))

    geoids_list = filter(lambda g: bool(g), geoids.split(','))
    for g in utils.fetch_geographies(geoids_list):
        csvrow = _csv_row_for_geography(g, tables)
        w.writerow(csvrow)

    now = datetime.now()
    date_string = "%s-%s-%s-%s" % (now.year, now.month, now.day, now.microsecond)
    response['Content-Disposition'] = "attachment; filename=ire-census-%s.csv" % date_string

    return response


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
        tables_list = mongoutils.get_tables()
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
        labels = mongoutils.get_labels_for_table(table)
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
