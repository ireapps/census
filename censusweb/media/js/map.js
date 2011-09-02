$(function(){
    
function coords_to_paths(coords) {
    // Construct new polygons
    var paths = [];
    var bounds = null;

    $.each(coords, function(i, n){
        $.each(n, function(j, o){
            var path = [];

            $.each(o, function(k,p){
                var ll = new L.LatLng(p[1], p[0]);
                path.push(ll);

                if (bounds === null) {
                    bounds = new L.LatLngBounds(ll, ll);
                } else {
                    bounds.extend(ll);
                }
            });

            paths.push(path);
        });
    });
    return {
        'paths': paths,
        'bounds': bounds
    };
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

window.map = null;    
function init_map(lat, lng) {
    if (window.map == null) {
        if (lat == null || lng == null) {
            lat = 41.882087;
            lng = -87.627799;
        }  
        var ll = new L.LatLng(lat, lng);

        window.map = new L.Map('map', {
            zoom: 14,
            center: ll,
        });

        tiles = new L.TileLayer("http://mt1.google.com/vt/lyrs=m@155000000&hl=en&x={x}&y={y}&z={z}&s={s}", {
            maxZoom: 17,
            attribution: "Map data is Copyright Google, 2011"
        });

        window.map.addLayer(tiles);
        var geoids = parseGeoids();
        for (var i = 0; i < geoids.length; i++) {
            add_boundary(geoids[i]);
        }
    }

}    
window.add_boundary = function(geoid) {
    ire_census.get_geojson(geoid,function(geojson) {
        window.stash = geojson;
        var x = coords_to_paths(geojson['simple_shape']['coordinates']);
        displayed_polygon = new L.Polygon(x.paths, {
            color: "#244f79",
            opacity: 0.8,
            weight: 3,
            fill: true,
            fillColor: "#244f79",
            fillOpacity: 0.2
        });

        map.addLayer(displayed_polygon);
        map.fitBounds(x.bounds);
    });
}
$(document).ready(init_map);

});
