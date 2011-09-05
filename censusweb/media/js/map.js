$(function(){
    var geocoder = new google.maps.Geocoder();    
    window.map = null;    
    window.boundary_layers = {};
    window.bounds = null;

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

    function leaflet_bounds_from_google_viewport(viewport) {
        var top_left = new L.LatLng(viewport.getNorthEast().lat(), viewport.getSouthWest().lng());
        var bottom_right = new L.LatLng(viewport.getSouthWest().lat(),viewport.getNorthEast().lng())
        return new L.LatLngBounds(top_left, bottom_right);
    }

    function leaflet_point_from_google_point(location) {
        return new L.LatLng(location.lat(),location.lng());
    }

    window.remove_all_layers = function(map) {
        if (map == null) {
            map = window.map;
        }
        for (var geoid in window.boundary_layers) {
            var layer = window.boundary_layers[geoid]
            map.removeLayer(layer);
            delete window.boundary_layers[geoid];
        }
    }

    function handle_geocode(result) {
        var point = leaflet_point_from_google_point(result.geometry.location);
        place_marker(point);
        window.shapes = [];
        window.map.panTo(point);
        window.map.fitBounds(leaflet_bounds_from_google_viewport(result.geometry.viewport));
        contains_opts = {}
        if ($("#types").val()) {
            contains_opts['sets'] = $("#types").val();
        }
        ire_census.do_with_contains_results([point.lat,point.lng],function(results) {
            remove_all_layers(window.map);
            var geoids = [];
            _.each(results.objects,function(census_shape) {
                geoids.push(census_shape.external_id);
                window.add_boundary(census_shape,true);
            })
        
            geoids.sort();
            try {
                history.pushState({},result.address_components[0].long_name,"/map/" + geoids.join(',') + ".html")
            } catch(e) {
                // no history... skip for now
            }
            window.location.hash = result.geometry.location.lat() + "," + result.geometry.location.lng();
        }, contains_opts);
    }

    window.place_marker = function(ll) {
        if (window.marker) {
            window.map.removeLayer(window.marker);
            window.marker = null;
        }
        var marker = new L.Marker(ll, { draggable: false });
        window.map.addLayer(marker);
        window.marker = marker;
    }

    function init_map() {
        if (window.map == null) {
            var marker_at_center = false;
        
            if (window.location.hash) {
                var locstr = window.location.hash.substr(1);
                parts = locstr.split(',');
                lat = parseFloat(parts[0]);
                lng = parseFloat(parts[1]);
                marker_at_center = true;
            } else {
                lat = 41.882087;
                lng = -87.627799;
            }

            var ll = new L.LatLng(lat, lng);

            window.map = new L.Map('map', {
                zoom: 14,
                center: ll,
            });

            if (marker_at_center) {
                place_marker(ll);
            }

            tiles = new L.TileLayer("http://mt1.google.com/vt/lyrs=m@155000000&hl=en&x={x}&y={y}&z={z}&s={s}", {
                maxZoom: 17,
                attribution: "Map data is Copyright Google, 2011"
            });

            window.map.addLayer(tiles);
            var geoids = parseGeoids();
            for (var i = 0; i < geoids.length; i++) {
                if (geoids[i]) {
                    ire_census.do_with_geodata(geoids[i],window.add_boundary);
                }
            }
        
        }
    
    }    
    window.add_boundary = function(geojson,fit_bounds) {
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
        window.boundary_layers[geojson.external_id] = displayed_polygon;
        if (window.bounds == null) {
            window.bounds = x.bounds;
        } else {
            window.bounds.extend(x.bounds.getNorthEast());
            window.bounds.extend(x.bounds.getSouthWest());
        }
        if (fit_bounds) {
            map.fitBounds(x.bounds);
        }
    }
    $(document).ready(function() {
        init_map();
        $("#geocoder").geocodify({
                onSelect: handle_geocode,
                regionBias: 'us',
                filterResults: function(results) {
                    var filteredResults =[];
                    $.each(results, function(i,val) {
                        for (var ac in val.address_components) {
                            for (var t in val.address_components[ac].types) {
                                if (val.address_components[ac].types[t] === 'country') {
                                    if (val.address_components[ac].short_name === 'US' || val.address_components[ac].short_name === 'PR') {
                                        filteredResults.push(val);
                                    }
                                }
                            }
                        }
                    });
                    return filteredResults;
                }
        });
    });

});
