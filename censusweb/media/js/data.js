$(function(){
    var dataset = "SF1";

    window.apiRequest = function(path, callback, handler) {
        $.ajax(API_URL + path, {
            dataType: "jsonp",
            jsonpCallback: callback,
            success: handler
        });
    }

    window.loadLabels = function() {
        apiRequest(dataset + "_labels.jsonp", "labels_" + dataset, function(labels_data) {
            // TODO - get geoids from url
            geoids = ["10"];

            //var tables = _.keys(labels_data["tables"]);
            //tables.sort();
            tables = ["P1"];

            var geographies = new Array();

            _.each(geoids, function(geoid) {
                apiRequest(geoid + ".jsonp", "geoid_" + geoid, function(geography_data) {
                    geographies.push(geography_data);

                    // If all geographies have been loaded, make reports
                    if (geographies.length == geoids.length) {
                        _.each(tables, function(table) {
                            labelset =  labels_data["tables"][table];
                            makeReport(table, labelset, geographies);
                        });
                    }
                });
            });
        });
    }

    window.makeReport = function(table, labelset, geographies) {
        report = {
            'key': labelset["key"],
            'name': labelset['name'],
            'table': labelset["key"] + ". " + labelset['name'],
            'universe': labelset['universe'],
            'columns': [],
            'rows': []
        };

        labels = labelset["labels"];

        _.each(labels, function(label) {
            row = {
                "key": label["key"],
                "label": label,
                "data": []
            }

            _.each(geographies, function(geography) {
                d = {};
                _.each(['2000','2010','delta','pct_change'], function(year) {
                    try {
                        d[year] = geography["data"][year][table_name][label["key"]];
                    } catch(err) {
                    }
                });

                row["data"].push(d);
            });

            report["rows"].push(row);
        });

        _.each(geographies, function(geography) {
            column_meta = {};
            column_name = geography["metadata"]["NAME"];

            // TODO
            if ($.inArray(geography["sumlev"], [SUMLEV_COUNTY, SUMLEV_PLACE, SUMLEV_TRACT])) {
                column_name += ", TODO"; 
            }

            column_meta["name"] = column_name;
            column_meta["geoid"] = geography["geoid"];
            column_meta["sumlev"] = geography["sumlev"];

            report["columns"].push(column_meta);
        });

        // TODO
        report["geoid_list"] = ["10"];
        report["show_remove_button"] = true;

        var template = template = _.template($('#report-template').html());
        var html = template(report);

        $('#table-container').before(html);
    }

    // Kick-off
    loadLabels();
});
