$(function(){
    init_state_menu = function(init_val) {
        ire_census.do_with_available_states(function(states) {
            _(states).each(function(s) { 
                $("#state-download").append("<option value='"+ ire_census.STATE_FIPS[s] + "'>" + s + " ("+ire_census.STATE_FIPS[s]+")</option>");
            });
            if(init_val) {
                $("#state-download").val(init_val);
            }
            
        })
    }
    
    init_sumlev_menu = function(init_val) {
        _(SUMLEVS).each(function(s) { 
            $("#sumlev-download").append("<option value='"+ s[0] + "'>" + s[1] + " ("+s[0]+")</option>");
            if (init_val) {
                $("#sumlev-download").val(init_val);
            }
        });
    }

    init_table_menu = function(init_val) {
        ire_census.do_with_labels(function(labels_data) {
            tables = _.keys(labels_data["tables"])
            tables = _.sortBy(window.tables, ire_census.table_comparator);
            _(tables).each(function(table_id) {
                $("#table-download").append("<option value='"+ table_id + "'>"+table_id+". "+ labels_data["tables"][table_id]["name"] +"</option>");
            });
            if (init_val) {
                $("#table-download").val(init_val);
            }
        });
    }

    download_based_on_form_values = function() {
        var track = [$("#state-download").val(),$("#sumlev-download").val(),$("#table-download").val()].join("-");
        _gaq.push(['_trackEvent', 'BulkDownload', track]);
        window.location.href = ire_census.build_bulk_data_url($("#state-download").val(),$("#sumlev-download").val(),$("#table-download").val(),"csv");
        return false;
    };
    download_shapefile_based_on_form_values = function() {
        var track = [$("#state-download").val(),$("#sumlev-download").val()].join("-");
        _gaq.push(['_trackEvent', 'ShapefileDownload', track]);
        window.location.href = ire_census.build_shapefile_url($("#state-download").val(),$("#sumlev-download").val());
    }

    parse_params = function() {
        var params = new Array();
        var query = window.location.search.substring(1);
        var qsplit = query.split('&');
        for (var i=0; i<qsplit.length; i++) {
            var pos = qsplit[i].indexOf('=');
            if (pos > 0) {
                var key = qsplit[i].substring(0,pos);
                var val = qsplit[i].substring(pos+1);
                params[key] = val;
            }
        }
        return params;
    }

    init_bulk_data = function() {
        params = parse_params();
        init_state_menu(params['state']);
        init_sumlev_menu(params['sumlev']);
        init_table_menu(params['table']);
        $("#start-download").click(download_based_on_form_values);
        $("#shapefile-download").click(download_shapefile_based_on_form_values);
    };
    
    init_bulk_data();
});
