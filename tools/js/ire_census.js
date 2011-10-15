// Dependencies:
// jQuery
var ire_census = {};
(function() { 
    this.API_URL = "http://censusdata.ire.org"
    this.GEOAPI_URL = "http://census.ire.org/geo/1.0"
    
    function apiRequest(path, callback, handler) {
        var api_url = this.API_URL;
        console.log("apiRequest: " + api_url);
        $.ajax(api_url + path, {
            dataType: "jsonp",
            jsonpCallback: callback,
            success: handler
        });
    }

    this.table_comparator = function (table) {
        parts = table.match(/([A-Z]+)(\d+)([A-Z]+)?/);

        key = parts[1];
        num = parts[2];

        if (key[0] == 'P') {
            key = "A" + key; // sort P tables first as Census does
        }   
        while (num.length < 3) {
            num = '0' + num;
        }

        key += num;

        if (parts[3]) {
            key += parts[3];
        }

        return key; 
    }

    this.table_from_field = function(field_code) {
        parts = field_code.match(/^(H|P|HCT|PCT|PCO)(\d{3})(\D)?(\d{3})$/i);
        if (!parts) throw "Invalid field code."
        while (parts[2][0] == '0') parts[2] = parts[2].substr(1);
        return parts.slice(1,4).join('').toUpperCase();
    }

    this.build_bulk_data_url = function(state,sumlev,table,format) {
        if (!format) {
            format = 'csv';
        }
        if (table) {
            table = "." + table;
        } else {
            table = "";
        }
        return this.API_URL + "/" + state + "/all_" + sumlev + "_in_"+state+table+"." + format;
    }

    this.build_shapefile_url = function(state,sumlev) {
        for (var i = 0; i < SUMLEVS.length; i++) {
            if (SUMLEVS[i][0] == sumlev) {
                url_parts = [SUMLEVS[i][2][0],state,SUMLEVS[i][2][1]]
                return url_parts.join('');
            }
        }
        throw "Invalid summary level";
    }

    this.do_with_available_states = function(handler) {
        apiRequest("/states.jsonp", "states", handler);
    }

    this.do_with_labels = function(handler,options) {
        opts = { 'dataset': 'SF1'} // at this time there are no plans to include other datasets in the IRE app, so this may go away.
        $.extend(opts,options);
        apiRequest("/" + opts.dataset + "_labels.jsonp", "labels_" + opts.dataset, handler);
    }

    this.do_with_sf1_data = function(geoid, handler) {
        var state = geoid.substring(0, 2);
        apiRequest("/" + state + "/" + geoid + ".jsonp", "geoid_" + geoid, handler);
    }
    
    GEOGRAPHY_TYPES = [
        [/^\d{11}$/,'tracts'],
        [/^\d{10}$/,'county-subdivisions'],
        [/^\d{5}$/,'counties'],
        [/^\d{2}$/,'states'],
        [/^\d{7}$/,'places']
    ];
    
    // do_with_geodata: for a string representing a single location, fetch the JSON data (including GeoJSON) 
    // from GEOAPI_URL and pass it to success_handler.
    // For now, if geoid begins with a slash, it will be treated as a complete type/geoid combo. This
    // leaves it fairly flexible to add more geographies in case sometimes lengths aren't distinctive. 
    // But also for now, we can infer the geography type by the length of the geoID, so the value for 
    // geoid may also simply be a string of 2-11 digits, or technically any pattern defined in GEOGRAPHY_TYPES.
    //
    // See http://census.ire.org/docs/boundary.html for more on the API, or to see what data
    // gets returned, look at http://census.ire.org/geo/1.0/boundary-set/places/1714000
    // TK: examples demonstrating how to put the shape which is returned on a map.
    this.do_with_geodata = function (geoid,success_handler) {
        if (geoid[0] != '/') {
            var matched = false;
            for (var i=0; i < GEOGRAPHY_TYPES.length; i++) {
                if (geoid.match(GEOGRAPHY_TYPES[i][0])) {
                    geoid = "/" + GEOGRAPHY_TYPES[i][1] + "/" + geoid;
                    matched = true;
                    break;
                }
            }
            if (!matched) {
                throw "Geoid does not match any known types. Check the length."
            }
        }
        if (geoid.substr(0,'/boundary-set'.length) != '/boundary-set') {
            geoid = '/boundary-set' + geoid;
        }
        $.ajax(this.GEOAPI_URL + geoid, {
            dataType: "jsonp",
            success: success_handler
        });
    }
    
    // given a point as [lat,lng] or as "lat,lng", call the contains function at GEOAPI_URL and pass the results 
    // to success_handler. not rigged to handle paginated results, but for foreseeable future, 
    // the contains query won't return enough for that to matter. 
    this.do_with_contains_results = function(point,success_handler,options) {
        if ($.isArray(point)) {
            point = point.join(',');
        }
        var url = '/boundary/?contains=' + point;
        if (options && options.sets) {
            if ($.isArray(options.sets)) {
                url += "&sets=" + options.sets.join(',');
            } else {
                url += "&sets=" + options.sets;
            }
        }
        // 38.948337,-92.328032&sets=tracts,counties
        $.ajax(this.GEOAPI_URL + url, {
            dataType: "jsonp",
            success: success_handler
        });

        
    };

    // Given a JSON object of the typical structure returned from the do_with_sf1_data AJAX call,
    // return a simple field value. Just makes some things a little more concise.
    this.sf1val = function(sf1_json,field,year_or_cat) {
        var year_or_cat = year_or_cat || '2010';
        var table = this.table_from_field(field);
        return sf1_json.data[year_or_cat][table][field];
    }

    // Given a JSON object of the typical structure returned from the do_with_sf1_data AJAX call,
    // return a field value as a percentage of total population or housing units (as appropriate for the field)
    // if this is to "work" for 'delta' or 'pct_change' special handling should be added. For now it's naive and 
    // thus probably wrong...
    this.sf1val_pct = function(sf1_json,field,year_or_cat) {
        var year_or_cat = year_or_cat || '2010';
        var val = parseFloat(this.sf1val(sf1_json,field,year_or_cat))
        var denom_field = (field.toUpperCase()[0] == 'H') ? "H001001" : "P001001";
        var denom_val = parseFloat(this.sf1val(sf1_json,denom_field,year_or_cat));
        return val / denom_val * 100;
    }

    this.table_name = function(label_data, table_code) {
        return label_data['tables'][table_code]['name'];
    }

    this.table_universe = function(label_data, table_code) {
        return label_data['tables'][table_code]['universe'];
    }

    this.table_size = function(label_data, table_code) {
        return label_data['tables'][table_code]['size'];
    }

    this.label_text = function(label_data, field_code) {
        var table_code = this.table_from_field(field_code);
        return label_data['tables'][table_code]['labels'][field_code]['text']
    }

    this.STATE_FIPS = {
        "Alabama": "01",
        "Alaska": "02",
        "Arizona": "04",
        "Arkansas": "05",
        "California": "06",
        "Colorado": "08",
        "Connecticut": "09",
        "Delaware": "10",
        "District of Columbia": "11",
        "Florida": "12",
        "Georgia": "13",
        "Hawaii": "15",
        "Idaho": "16",
        "Illinois": "17",
        "Indiana": "18",
        "Iowa": "19",
        "Kansas": "20",
        "Kentucky": "21",
        "Louisiana": "22",
        "Maine": "23",
        "Maryland": "24",
        "Massachusetts": "25",
        "Michigan": "26",
        "Minnesota": "27",
        "Mississippi": "28",
        "Missouri": "29",
        "Montana": "30",
        "Nebraska": "31",
        "Nevada": "32",
        "New Hampshire": "33",
        "New Jersey": "34",
        "New Mexico": "35",
        "New York": "36",
        "North Carolina": "37",
        "North Dakota": "38",
        "Ohio": "39",
        "Oklahoma": "40",
        "Oregon": "41",
        "Pennsylvania": "42",
        "Puerto Rico": "72",
        "Rhode Island": "44",
        "South Carolina": "45",
        "South Dakota": "46",
        "Tennessee": "47",
        "Texas": "48",
        "Utah": "49",
        "Vermont": "50",
        "Virginia": "51",
        "Washington": "53",
        "West Virginia": "54",
        "Wisconsin": "55",
        "Wyoming": "56"
    }

    this.get_state_fips = function(state) {
        return this.STATE_FIPS[state];
    }

    this.FIPS_STATE = {}
    
    for (name in this.STATE_FIPS) {
        var fips = this.get_state_fips(name);
        this.FIPS_STATE[fips] = name;
    }
    
    this.get_fips_state = function(fips) {
        return this.FIPS_STATE[fips];
    }

    SUMLEVS = [
        // tuples: (code, name, shapefile_template)
        ['040','State', ["http://www2.census.gov/geo/tiger/TIGER2010/STATE/2010/tl_2010_","_state10.zip"]],
        ['050','County', ["http://www2.census.gov/geo/tiger/TIGER2010/COUNTY/2010/tl_2010_","_county10.zip"]],
        ['060','County Subdivision', ["http://www2.census.gov/geo/tiger/TIGER2010/COUSUB/2010/tl_2010_","_cousub10.zip"]],
        ['140','Census Tract', ["http://www2.census.gov/geo/tiger/TIGER2010/TRACT/2010/tl_2010_","_tract10.zip"]],
        ['160','Place', ["http://www2.census.gov/geo/tiger/TIGER2010/PLACE/2010/tl_2010_","_place10.zip"]]
    ]
}).apply(ire_census);
