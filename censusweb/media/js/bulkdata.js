$(function(){
    init_state_menu = function() {
        do_with_available_states(function(states) {
            _(states).each(function(s) { 
                $("#state-download").append("<option value='"+ STATES[s] + "'>" + s + " ("+STATES[s]+")</option>");
            });
        })
    }
    
    init_sumlev_menu = function() {
        _(SUMLEVS).each(function(s) { 
            $("#sumlev-download").append("<option value='"+ s[0] + "'>" + s[1] + " ("+s[0]+")</option>");
        });
    }

    init_table_menu = function() {
        do_with_labels(function(labels_data) {
            tables = _.keys(labels_data["tables"])
            tables = _.sortBy(window.tables, window.table_comparator);
            _(tables).each(function(table_id) {
                $("#table-download").append("<option value='"+ table_id + "'>"+table_id+". "+ labels_data["tables"][table_id]["name"] +"</option>");
            });
        });
    }

    download_based_on_form_values = function() {
        window.location.href = build_bulk_data_url($("#state-download").val(),$("#sumlev-download").val(),$("#table-download").val(),"csv");
        return false;
    };
    
    init_bulk_data = function() {
        init_state_menu();
        init_sumlev_menu();
        init_table_menu();
        $("#start-download").click(download_based_on_form_values);
    };
    
    init_bulk_data();
});
