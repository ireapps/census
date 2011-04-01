#!/usr/bin/env python
""" Convert remote U.S. Census 2000 data to local tab-separated text files.

Run with --help flag for usage instructions.
"""

from sys import stdout, stderr
from os import SEEK_SET, SEEK_CUR, SEEK_END
from re import compile
from time import time
from csv import reader, writer, DictReader
from os.path import basename
from datetime import timedelta
from optparse import OptionParser
from urlparse import urlparse, urljoin
from cStringIO import StringIO
from httplib import HTTPConnection
from urllib import urlopen
from zipfile import ZipFile
from itertools import izip

class RemoteFileObject:
    """ Implement enough of this to be useful:
        http://docs.python.org/release/2.5.2/lib/bltin-file-objects.html
        
        Pull data from a remote URL with HTTP range headers.
    """

    def __init__(self, url, verbose=False, block_size=(16 * 1024)):
        self.verbose = verbose

        # scheme://host/path;parameters?query#fragment
        (scheme, host, path, parameters, query, fragment) = urlparse(url)
        
        self.host = host
        self.rest = path + (query and ('?' + query) or '')

        self.offset = 0
        self.length = self.get_length()
        self.chunks = {}
        
        self.block_size = block_size
        self.start_time = time()

    def get_length(self):
        """
        """
        conn = HTTPConnection(self.host)
        conn.request('GET', self.rest, headers={'Range': '0-1'})
        length = int(conn.getresponse().getheader('content-length'))
        
        if self.verbose:
            print >> stderr, length, 'bytes in', basename(self.rest)

        return length

    def get_range(self, start, end):
        """
        """
        headers = {'Range': 'bytes=%(start)d-%(end)d' % locals()}

        conn = HTTPConnection(self.host)
        conn.request('GET', self.rest, headers=headers)
        return conn.getresponse().read()

    def read(self, count=None):
        """ Read /count/ bytes from the resource at the current offset.
        """
        if count is None:
            # to the end
            count = self.length - self.offset

        out = StringIO()

        while count:
            chunk_offset = self.block_size * (self.offset / self.block_size)
            
            if chunk_offset not in self.chunks:
                range = chunk_offset, min(self.length, self.offset + self.block_size) - 1
                self.chunks[chunk_offset] = StringIO(self.get_range(*range))
                
                if self.verbose:
                    loaded = float(self.block_size) * len(self.chunks) / self.length
                    expect = (time() - self.start_time) / loaded
                    remain = max(0, int(expect * (1 - loaded)))
                    print >> stderr, '%.1f%%' % min(100, 100 * loaded),
                    print >> stderr, 'of', basename(self.rest),
                    print >> stderr, 'with', timedelta(seconds=remain), 'to go'

            chunk = self.chunks[chunk_offset]
            in_chunk_offset = self.offset % self.block_size
            in_chunk_count = min(count, self.block_size - in_chunk_offset)
            
            chunk.seek(in_chunk_offset, SEEK_SET)
            out.write(chunk.read(in_chunk_count))
            
            count -= in_chunk_count
            self.offset += in_chunk_count

        out.seek(0)
        return out.read()

    def seek(self, offset, whence=SEEK_SET):
        """ Seek to the specified offset.
            /whence/ behaves as with other file-like objects:
                http://docs.python.org/lib/bltin-file-objects.html
        """
        if whence == SEEK_SET:
            self.offset = offset
        elif whence == SEEK_CUR:
            self.offset += offset
        elif whence == SEEK_END:
            self.offset = self.length + offset

    def tell(self):
        return self.offset

def file_choice(summary_file, tables, verbose):
    """
    """
    url = 'http://census-tools.teczno.com/%s.txt' % summary_file
    src = StringIO(urlopen(url).read())
    
    files = []
    
    for table in tables:
        src.seek(0)
        
        file_name, column_offset = None, 5
        
        for row in DictReader(src, dialect='excel-tab'):
            curr_file, curr_table, cell_count = row.get('File Name'), row.get('Matrix Number'), int(row.get('Cell Count'))
            
            if curr_file != file_name:
                file_name, column_offset = curr_file, 5
        
            if curr_table == table:
                if verbose:
                    print >> stderr, table, '-', row.get('Name'), 'in', row.get('Universe')
    
                files.append((table, file_name, column_offset, cell_count))
                break
            
            column_offset += cell_count
        
    return files

def file_paths(summary_file, state, file_names):
    """
    """
    file_paths_func = globals().get('_file_paths_%s' % summary_file)
    return file_paths_func(state, file_names)

def _file_paths_SF1(state, file_names):
    """
    """
    if state:
        dir_name = state.replace(' ', '_')
        state_prefix = states.get(state).lower()
        geo_path = 'Summary_File_1/%s/%sgeo_uf1.zip' % (dir_name, state_prefix)
        data_pat = 'Summary_File_1/%s/%s000%%s_uf1.zip' % (dir_name, state_prefix)
    
    else:
        geo_path = 'Summary_File_1/0Final_National/usgeo_uf1.zip'
        data_pat = 'Summary_File_1/0Final_National/us000%s_uf1.zip'

    data_paths = [(file_name, data_pat % file_name) for file_name in file_names]
    return geo_path, dict(data_paths)

def _file_paths_SF3(state, file_names):
    """
    """
    if state:
        dir_name = state.replace(' ', '_')
        state_prefix = states.get(state).lower()
        geo_path = 'Summary_File_3/%s/%sgeo_uf3.zip' % (dir_name, state_prefix)
        data_pat = 'Summary_File_3/%s/%s000%%s_uf3.zip' % (dir_name, state_prefix)
    
    else:
        geo_path = 'Summary_File_3/0_National/usgeo_uf3.zip'
        data_pat = 'Summary_File_3/0_National/us000%s_uf3.zip'

    data_paths = [(file_name, data_pat % file_name) for file_name in file_names]
    return geo_path, dict(data_paths)

def column_names(wide):
    """
    """
    if wide is True:
        return ['Summary Level', 'Geographic Component', 'State FIPS', 'Place FIPS', 'County FIPS', 'Tract', 'Zip', 'Block', 'Name', 'Latitude', 'Longitude', 'Land Area', 'Water Area', 'Population', 'Housing Units']
    elif wide is False:
        return ['State FIPS', 'Place FIPS', 'County FIPS', 'Tract', 'Zip', 'Block']
    else:
        return ['Summary Level', 'Geographic Component', 'State FIPS', 'Place FIPS', 'County FIPS', 'Tract', 'Zip', 'Block', 'Name', 'Latitude', 'Longitude']

def key_names(wide):
    """
    """
    if wide is True:
        return ('SUMLEV', 'GEOCOMP', 'STATE', 'PLACE', 'COUNTY', 'TRACT', 'ZCTA5', 'BLOCK', 'NAME', 'LATITUDE', 'LONGITUDE', 'AREALAND', 'AREAWATER', 'POP100', 'HU100')
    elif wide is False:
        return ('STATE', 'PLACE', 'COUNTY', 'TRACT', 'ZCTA5', 'BLOCK')
    else:
        return ('SUMLEV', 'GEOCOMP', 'STATE', 'PLACE', 'COUNTY', 'TRACT', 'ZCTA5', 'BLOCK', 'NAME', 'LATITUDE', 'LONGITUDE')

def geo_lines(path, verbose):
    """
    """
    u = urljoin('http://www2.census.gov/census_2000/datasets/', path)
    f = RemoteFileObject(u, verbose, 256 * 1024)
    z = ZipFile(f)
    n = z.namelist()
    
    assert len(n) == 1, 'Expected one file, not %d: %s' % (len(n), repr(n))
    
    # Offsets here are one-based to match the documentation in
    # http://census-tools.teczno.com/SF1-p015-34-geo-state.pdf
    cols = [('LATITUDE', 311, 9), ('LONGITUDE', 320, 10),
            ('LOGRECNO', 19, 7), ('SUMLEV', 9, 3), ('GEOCOMP', 12, 2),
            ('STATE', 30, 2), ('PLACE', 46, 5), ('COUNTY', 32, 3), ('TRACT', 56, 6),
            ('BLOCK', 63, 4), ('NAME', 201, 90), ('ZCTA3', 158, 3), ('ZCTA5', 161, 5),
            ('AREALAND', 173, 14), ('AREAWATER', 187, 14),
            ('POP100', 293, 9), ('HU100', 302, 9)]

    for line in z.open(n[0]):
        data = dict( [(key, line[s-1:s-1+l].strip()) for (key, s, l) in cols] )
        
        for key in ('LATITUDE', 'LONGITUDE'):
            val = data[key]
            data[key] = (val[0] + val[1:-6].lstrip('0') + '.' + val[-6:]).lstrip('+')
        
        #for key in ('AREALAND', 'AREAWATER', 'POP100', 'HU100'):
        #    data[key] = int(data[key])
        
        yield data

def data_lines(path, verbose):
    """
    """
    u = urljoin('http://www2.census.gov/census_2000/datasets/', path)
    f = RemoteFileObject(u, verbose, 256 * 1024)
    z = ZipFile(f)
    n = z.namelist()
    
    assert len(n) == 1, 'Expected one file, not %d: %s' % (len(n), repr(n))
    
    for row in reader(z.open(n[0])):
        yield row

summary_levels = {'country': '010', 'region': '020', 'state': '040', 'county': '050', 'tract': '080', 'zip': ('860', '871'), 'block': '101', 'place': '160'}

states = {'Alabama': 'AL', 'Alaska': 'AK', 'American Samoa': 'AS', 'Arizona': 'AZ',
    'Arkansas': 'AR', 'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'District of Columbia': 'DC', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY',
    'Louisiana': 'LA', 'Maine': 'ME', 'Marshall Islands': 'MH', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH',
    'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC',
    'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
    'Puerto Rico': 'PR', 'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
    'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA',
    'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'}

parser = OptionParser(usage="""%%prog [options] [list of table IDs]

Convert remote U.S. Census 2000 data to local tab-separated text files.

Examples:

    Housing basics for counties in Rhode Island
    census2text.py --state 'Rhode Island' H1 H3 H4
    
    Age breakdowns for census tracts around Oakland, CA
    census2text.py --state California --bbox 37.86 -122.35 37.70 -122.10 --geography tract P12
    
    Family type and employment state for counties around New England
    census2text.py --file SF3 --bbox 47.7 -80.7 38.4 -66.4 P44

Complete documentation of Summary File data is dense but helpful:
  http://www.census.gov/prod/cen2000/doc/sf1.pdf

See Chapter 7, page 228 for explanation of column names in output.

Other summary files have similar docs:
  http://www.census.gov/prod/cen2000/doc/sf3.pdf

Available summary files: SF1, SF3.

Available table IDs for each summary file:
  http://census-tools.teczno.com/SF1-p078-82-subject-locator.pdf
  http://census-tools.teczno.com/SF3-p062-84-subject-locator.pdf

Available summary levels: %s.

See also numeric summary levels in:
  http://census-tools.teczno.com/SF1-p083-84-sequence-state.pdf
  http://census-tools.teczno.com/SF1-p087-88-sequence-national.pdf

""".rstrip() % ', '.join(summary_levels.keys()))

parser.set_defaults(summary_file='SF1', summary_level='county', table='P1', verbose=None, wide=None)

parser.add_option('-o', '--output', dest='output',
                  help='Optional output filename, stdout if omitted.')

parser.add_option('-f', '--file', dest='summary_file',
                  help='Optional summary file, defaults to "SF1".',
                  type='choice', choices=('SF1', 'SF3'))

parser.add_option('-g', '--geography', dest='summary_level',
                  help='Geographic summary level, e.g. "state", "040". Some available summary levels are %s.' % ', '.join(summary_levels.keys()),
                  type='choice', choices=summary_levels.keys() + summary_levels.values())

parser.add_option('-s', '--state', dest='state',
                  help='Optional state, e.g. "Alaska", "District of Columbia".',
                  type='choice', choices=states.keys())

parser.add_option('-b', '--bbox', dest='bbox',
                  help='Optional geographic bounds: north west south east.',
                  type='float', nargs=4)

parser.add_option('-n', '--narrow', dest='wide',
                  help='Output fewer columns than normal',
                  action='store_false')

parser.add_option('-w', '--wide', dest='wide',
                  help='Output more columns than normal',
                  action='store_true')

parser.add_option('-q', '--quiet', dest='verbose',
                  help='Be quieter than normal',
                  action='store_false')

parser.add_option('-v', '--verbose', dest='verbose',
                  help='Be louder than normal',
                  action='store_true')

if __name__ == '__main__':

    options, tables = parser.parse_args()
    
    if options.summary_level in summary_levels:
        options.summary_level = summary_levels[options.summary_level]

    if type(options.summary_level) is not tuple:
        options.summary_level = (options.summary_level, )
    
    files = file_choice(options.summary_file, tables, options.verbose is not False)
    
    if options.verbose is not False:
        print >> stderr, ', '.join(options.summary_level), options.state, '-',
        print >> stderr, ', '.join( ['%s: file %s (%d @%d)' % (tbl, fn, cc, co) for (tbl, fn, co, cc) in files] )
        print >> stderr, '-' * 32
    
    file_names = set( [file_name for (tbl, file_name, co, cc) in files] )
    geo_path, data_paths = file_paths(options.summary_file, options.state, file_names)

    if options.bbox is not None:
        north = max(options.bbox[0], options.bbox[2])
        south = min(options.bbox[0], options.bbox[2])
        east = max(options.bbox[1], options.bbox[3])
        west = min(options.bbox[1], options.bbox[3])
        
    out = options.output and open(options.output, 'w') or stdout
    out = writer(out, dialect='excel-tab')
    
    row = column_names(options.wide)
    pat = compile(r'^([A-Z]+)(\d+)([A-Z]*)$')
    
    for (table, fn, co, cell_count) in files:
        row += ['%s%03d%s%03d' % (pat.sub(r'\1', table), int(pat.sub(r'\2', table)), pat.sub(r'\3', table), cell)
                for cell in range(1, cell_count + 1)]
    
    out.writerow(row)
    
    file_iters = {}
    
    for (tbl, file_name, co, cc) in files:
        if file_name not in file_iters:
            file_iters[file_name] = data_lines(data_paths[file_name], options.verbose)
    
    file_names = sorted(file_iters.keys())
    geo_iter = geo_lines(geo_path, options.verbose)
    
    for geo in geo_iter:
        
        if geo['SUMLEV'] not in options.summary_level:
            # This is not the summary level you're looking for.
            continue

        if geo['GEOCOMP'] != '00':
            # Geographic Component "00" means the whole thing,
            # not e.g. "01" for urban or "43" for rural parts.
            continue

        if options.bbox is not None:
            lat, lon = float(geo['LATITUDE']), float(geo['LONGITUDE'])
            
            if lat < south or north < lat or lon < west or east < lon:
                # This geography is outside the bounding box
                continue
    
        row = [geo[key] for key in key_names(options.wide)]
        
        data_iters = izip(*[file_iters[file_name] for file_name in file_names])
        
        for data_lines in data_iters:
            
            file_data = dict(zip(file_names, data_lines))
            
            logrecno_matches = [geo['LOGRECNO'] == data[4] for data in file_data.values()]
            
            if False in logrecno_matches:
                # Logical record numbers don't match, keep looking
                continue

            # A match!
            for (tbl, file_name, column_offset, cell_count) in files:
                data = file_data[file_name]
                row += data[column_offset:column_offset + cell_count]
            
            # Great move on to the next geo
            break
        
        out.writerow(row)
        stdout.flush()
