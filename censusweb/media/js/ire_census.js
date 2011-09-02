// Dependencies:
// jQuery
var ire_census = {};
(function() { 
    function apiRequest(path, callback, handler) {
        $.ajax(this.API_URL + path, {
            dataType: "jsonp",
            jsonpCallback: callback,
            success: handler
        });
    }

    this.API_URL = "http://censusdata.ire.org"
    this.GEOAPI_URL = "http://census.ire.org/geo/1.0"
    
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

        if (!_.isUndefined(parts[3])) {
            key += parts[3];
        }

        return key; 
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
                // uses underscore template
                return SUMLEVS[i][2]({'state_fips': state});
            }
        }
        throw "Invalid summary level";
    }

    this.do_with_available_states = function(handler) {
        apiRequest("/states.jsonp", "states", handler);
    }

    this.do_with_labels = function(handler) {
        apiRequest("/" + window.DATASET + "_labels.jsonp", "labels_" + window.DATASET, handler);
    }

    this.do_with_sf1_data = function(geoid, callback) {
        var state = geoid.substring(0, 2);
        apiRequest("/" + state + "/" + geoid + ".jsonp", "geoid_" + geoid, callback);
    }
    
    GEOGRAPHY_TYPES = [
        [/^\d{11}$/,'tracts'],
        [/^\d{10}$/,'county-subdivisions'],
        [/^\d{5}$/,'counties'],
        [/^\d{2}$/,'states'],
        [/^\d{7}$/,'places']
    ];
    // For now, if geoid begins with a slash, it will be treated as a complete type/geoid combo. This
    // leaves it fairly flexible to add more geographies in case sometimes lengths aren't distinctive. 
    // But also for now, we can infer the geography type by the length of the geoID, so the value for 
    // geoid may also simply be a string of 2-11 digits, or technically any pattern defined in GEOGRAPHY_TYPES.
    //
    // See http://census.ire.org/docs/boundary.html for more on the API, or to see what data
    // gets returned, look at http://census.ire.org/geo/1.0/boundary-set/places/1714000
    // TK: examples demonstrating how to put the shape which is returned on a map.
    this.get_geojson = function (geoid,success_handler) {
        if (geoid[0] != '/') {
            for (var i=0; i < GEOGRAPHY_TYPES.length; i++) {
                if (geoid.match(GEOGRAPHY_TYPES[i][0])) {
                    geoid = "/" + GEOGRAPHY_TYPES[i][1] + "/" + geoid;
                    break
                }
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
        ['040','State', _.template("http://www2.census.gov/geo/tiger/TIGER2010/STATE/2010/tl_2010_<%=state_fips%>_state10.zip")],
        ['050','County', _.template("http://www2.census.gov/geo/tiger/TIGER2010/COUNTY/2010/tl_2010_<%=state_fips%>_county10.zip")],
        ['060','County Subdivision', _.template("http://www2.census.gov/geo/tiger/TIGER2010/COUSUB/2010/tl_2010_<%=state_fips%>_cousub10.zip")],
        ['140','Census Tract', _.template("http://www2.census.gov/geo/tiger/TIGER2010/TRACT/2010/tl_2010_<%=state_fips%>_tract10.zip")],
        ['160','Place', _.template("http://www2.census.gov/geo/tiger/TIGER2010/PLACE/2010/tl_2010_<%=state_fips%>_place10.zip")]
    ]
}).apply(ire_census);
