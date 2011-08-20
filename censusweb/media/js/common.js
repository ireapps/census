function table_comparator (table) {
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
    
function build_bulk_data_url(state,sumlev,table,format) {
    if (!format) {
        format = 'csv';
    }
    if (table) {
        table = "." + table;
    } else {
        table = "";
    }
    return API_URL + "/" + state + "/all_" + sumlev + "_in_"+state+table+"." + format;
}

function build_shapefile_url(state,sumlev) {
    for (var i = 0; i < SUMLEVS.length; i++) {
        if (SUMLEVS[i][0] == sumlev) {
            return SUMLEVS[i][2]({'state_fips': state});
        }
    }
    throw "Invalid summary level";
}

function apiRequest(path, callback, handler) {
    $.ajax(API_URL + path, {
        dataType: "jsonp",
        jsonpCallback: callback,
        success: handler
    });
}

function do_with_available_states(handler) {
    apiRequest("/states.jsonp", "states", handler);
}

function do_with_labels(handler) {
    apiRequest("/" + window.DATASET + "_labels.jsonp", "labels_" + window.DATASET, handler);
}

function do_with_sf1_data(geoid, callback) {
    var state = geoid.substring(0, 2);
    apiRequest("/" + state + "/" + geoid + ".jsonp", "geoid_" + geoid, callback);
}
STATES = {
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

SUMLEVS = [
    // tuples: (code, name, shapefile_template)
    ['040','State', _.template("http://www2.census.gov/geo/tiger/TIGER2010/STATE/2010/tl_2010_<%=state_fips%>_state10.zip")],
    ['050','County', _.template("http://www2.census.gov/geo/tiger/TIGER2010/COUNTY/2010/tl_2010_<%=state_fips%>_county10.zip")],
    ['060','County Subdivision', _.template("http://www2.census.gov/geo/tiger/TIGER2010/COUSUB/2010/tl_2010_<%=state_fips%>_cousub10.zip")],
    ['140','Census Tract', _.template("http://www2.census.gov/geo/tiger/TIGER2010/TRACT/2010/tl_2010_<%=state_fips%>_tract10.zip")],
    ['160','Place', _.template("http://www2.census.gov/geo/tiger/TIGER2010/PLACE/2010/tl_2010_<%=state_fips%>_place10.zip")]
]