$(function(){
    var basic_info_template = _.template($('#basic-info').html());
    window.parseGeoid = function() {
        // Get url without hashbang
        var target = _.last(window.location.pathname.split("/"));

        // Ditch the .html
        target = _.first(target.split("."));

        // Split the list
        geoids = target.split(",");

        return geoids[0];
    }

    function display_sf1_data(result) {
        console.log("in display_sf1_data");
        window.sf1 = result; // handy while developing...
        $("#profile").append(basic_info_template({'sf1json': result, 'ire_census': ire_census }));
    }

    function display_geodata(geodata) {
        console.log("in display_geodata");
        window.geodata = geodata;  // handy while developing...
        if (geodata.objects) {
            console.log("display_geodata: " + geodata.objects[0].external_id);
        }
    }

    $(document).ready(function(){
        var geoid = window.parseGeoid();
        ire_census.do_with_sf1_data(geoid,display_sf1_data);
        ire_census.do_with_geodata(geoid,display_geodata);
    });
});