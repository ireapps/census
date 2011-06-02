$(function(){
    var dataset = "PL";
    var report_template = _.template($('#report-template').html());

    removeColumn = function() {
        geoid = $(this).attr('data-val');
        if (document.location.pathname.indexOf('/' + geoid) > 0) {
            document.location.pathname = document.location.pathname.replace(geoid + ',', '');
        } else {
            document.location.pathname = document.location.pathname.replace(',' + geoid, '');
        }
    }
    
    twistRow = function() {
        var show_child = !$($('tr[parent=' + $(this).attr('id') + ']')[0]).is(":visible");
        twistRowHelper($(this), show_child);
        $(this).toggleClass('closed')
        $(this).toggleClass('open');
    }
    
    twistRowHelper = function(parent_row, show_me) {
        $.each($('tr[parent=' + $(parent_row).attr('id') + ']'), function(index, value){
            if(show_me){
                $(value).show();
            } else {
                $(value).hide();
            }
            twistRowHelper(value, false);
        });
    }
    
    addRelatedState = function() {
        this_geoid = $(this).attr('data-val');
        state_geoid = this_geoid.slice(0,2);
        
        window.location.pathname = window.location.pathname.replace('.html', "," + state_geoid + '.html');
    }

    addRelatedCounty = function() {
        this_geoid = $(this).attr('data-val');
        county_geoid = this_geoid.slice(0,5);
        
        window.location.pathname = window.location.pathname.replace('.html', "," + county_geoid + '.html');
    }

    window.apiRequest = function(path, callback, handler) {
        $.ajax(API_URL + path, {
            dataType: "jsonp",
            jsonpCallback: callback,
            success: handler
        });
    }

    window.parseGeoids = function() {
        // Get url without hashbang
        var target = _.last(window.location.pathname.split("/"));

        // Ditch the .html
        target = _.first(target.split("."));

        // Split the list
        geoids = target.split(",");

        return geoids;
    }

    window.parseTables = function() {
        //TODO - get tables from hash;
        var tables = ["P2"];
        tables.sort();

        return tables;
    }

    window.loadLabels = function() {
        apiRequest(dataset + "_labels.jsonp", "labels_" + dataset, function(labels_data) {
            var geoids = parseGeoids();
            //var tables = parseTables();

            var tables = _.keys(labels_data["tables"])
            tables.sort();

            var geographies = new Array();

            _.each(geoids, function(geoid) {
                apiRequest(geoid + ".jsonp", "geoid_" + geoid, function(geography_data) {
                    geographies.push(geography_data);

                    // If all geographies have been loaded, make reports
                    if (geographies.length == geoids.length) {
                        _.each(tables, function(table) {
                            var labelset =  labels_data["tables"][table];
                            var report = makeReport(table, labelset, geoids, geographies);
                            renderReport(report);
                        });
                        
                        configureEvents();
                    }
                });
            });
        });
    }

    window.makeReport = function(table, labelset, geoids, geographies) {
        var report = {
            'key': labelset["key"],
            'name': labelset['name'],
            'table': labelset["key"] + ". " + labelset['name'],
            'universe': labelset['universe'],
            'columns': [],
            'rows': []
        };

        var labels = _.sortBy(labelset["labels"], function(label) {
            return label["key"];
        });

        _.each(labels, function(label) {
            row = {
                "key": label["key"],
                "label": label,
                "data": [] 
            }

            _.each(geographies, function(geography) {
                var d = new Object();

                _.each(["2000", "2010", "delta", "pct_change"], function(year) {
                    try {
                        d[year] = geography["data"][year][table][label["key"]];
                    } catch(err) {
                    }
                });

                row["data"].push(d);
            });

            report["rows"].push(row);
        });

        _.each(geographies, function(geography) {
            var column_meta = {};
            column_name = geography["metadata"]["NAME"];

            // TODO
            if ($.inArray(geography["sumlev"], [SUMLEV_COUNTY, SUMLEV_PLACE, SUMLEV_TRACT]) >= 0) {
                column_name += ", TODO"; 
            }

            column_meta["name"] = column_name;
            column_meta["geoid"] = geography["geoid"];
            column_meta["sumlev"] = geography["sumlev"];

            report["columns"].push(column_meta);
        });

        report["geoids"] = geoids;
        report["show_remove_button"] = (geoids.length > 1);

        return report;
    }

    window.floatFormat = function(n, decimals) {
        if (_.isString(n)) {
            try {
                n = parseFloat(n);
            } catch(err) {
                return "";
            }
        }

        if (_.isUndefined(n) || _.isNaN(n)) {
            return "";
        }

        if (n % 1 == 0) {
            return Math.round(n);
        }

        if (_.isUndefined(decimals)) {
            decimals = 1;
        }

        pow = Math.pow(10, decimals);

        return Math.round(n * pow) / pow;
    }

    window.toPercent = function(n) {
        if (_.isString(n)) {
            try {
                n = parseFloat(n);
            } catch(err) {
                return "";
            }
        }

        if (_.isUndefined(n) || _.isNaN(n)) {
            return "";
        }

        return n * 100;
    }

    window.intComma = function(n) {
        // Algorithm from Django template tags
        // http://code.djangoproject.com/svn/django/trunk/django/contrib/humanize/templatetags/humanize.py
        if (_.isUndefined(n) || _.isNaN(n)) {
            return "";
        }

        orig = n
        n = n.toString().replace(/^(-?\d+)(\d{3}\.?\d*)/g, "$1,$2");

        if (n == orig) {
            return n;
        } else {
            return intComma(n);
        }
    }

    window.renderReport = function(report) {
        var html = report_template(report);

        $('#reports').append(html);
    }

    window.configureEvents = function() {
        // Add event hooks
        $('.button.remove-column').click(removeColumn);
        $('tr.row').click(this.twistRow);
        $('.button.add-related-state').click(this.addRelatedState);
        $('.button.add-related-county').click(this.addRelatedCounty);

        // Table mouseover row highlighting.
        $(".report").delegate('td', 'mouseover mouseleave', function(e) {
            if (e.type == 'mouseover') {
                status = ''
                $(this).addClass("selected");
                $(this).parent().addClass("highlight");
                status = $(this).parent().find('.label').text();
                if ($(this).index() > 0) {
                    $("colgroup", $(this).parents("table")).eq($(this).index()).addClass("highlight"); //column
                    status += ', ' + $($(this).parents("table").find('.locationdef')[Math.ceil($(this).index()/4) - 1]).clone().find('*').remove().end().text().trim();
                    status += ', ' + $($(this).parents("table").find('.subhead')[$(this).index() - 1]).text().trim();
                }
                $('#status').show().text(status);
            } else {
                $(this).removeClass("selected");
                $(this).parent().removeClass('highlight');
                if ($(this).index() > 0)
                    $("colgroup", $(this).parents("table")).eq($(this).index()).removeClass("highlight");
                $('#status').hide();
            }
        });
    }

    // Kick-off
    loadLabels();
});
