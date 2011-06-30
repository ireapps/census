$(function(){

    // ------------------------- Constants -----------------------------------
    SUMLEV_NATION = '010';
    SUMLEV_STATE = '040';
    SUMLEV_COUNTY = '050';
    SUMLEV_COUNTY_SUBDIVISION = '060';
    SUMLEV_TRACT = '140';
    SUMLEV_PLACE = '160';
    SUMLEV_BLOCK = '101';

    // ------------------------- Query Model ---------------------------------

    window.Query = Backbone.Model.extend({

        initialize: function() {
            _.bindAll(this, 'keypress', 'render', 'showHelp', 'loadNext', 'go');
            this.template = _.template($('#query-template').html());
            this.lazyRender = _.debounce(this.render, 50);
            this.filter = '';
            if ($.browser.ie) {
                $(document.body).keypress(this.keypress);
            } else {
                $(document).keypress(this.keypress);
            }

            $(document).keydown(this.keydown);
            this.bind('change', this.render);
            //this.bind('change', this.loadNext);
            this.mappings.summarylevelDisplays[SUMLEV_TRACT] = 'Tracts';
            this.mappings.summarylevelDisplays[SUMLEV_PLACE] = 'Places';
            this.mappings.summarylevelDisplays[SUMLEV_COUNTY] = 'Counties';
            this.mappings.summarylevelDisplays[SUMLEV_COUNTY_SUBDIVISION] = 'County Subdivisions';
            this.mappings.summarylevelDisplays[SUMLEV_STATE] = 'States';
            this.mappings.summarylevelDisplays[SUMLEV_NATION] = 'USA';

            availableStates(function(states) {
                _.each(states, function(state) {
                    query.mappings.states.push([state, STATES[state]]);
                });
            })
        },

        render: function() {
            // Remove this section to enable "go button" prompt:
            if (this.get('summarylevel') && this.get(this.get("summarylevel")))
                // Don't re-render. We just selected the item we wanted so
                // we are going to force "go" there. (See `select`.)
                return;

            $("#search").html(this.template({query: this}));
            $('#filter-help').toggle(!!this.shouldShowFilterHelp());
            $('#filter-display').toggle(!!this.filter).text(this.filterDisplay());
            $('#help-link').click(this.showHelp);
            $("#summarylevel-select .link").click(_.bind(this.select, this, 'summarylevel'));
            $("#state-select .link").click(_.bind(this.select, this, SUMLEV_STATE));
            $('#county-select .link').click(_.bind(this.select, this, SUMLEV_COUNTY));
            $('#county-subdivision-select .link').click(_.bind(this.select, this, SUMLEV_COUNTY_SUBDIVISION));
            $('#place-select .link').click(_.bind(this.select, this, SUMLEV_PLACE));
            $('#tract-select .link').click(_.bind(this.select, this, SUMLEV_TRACT));
            $('.button.go').click(this.go);
            $('.button.csv-json').click(this.csvJson);

        },

        isCompletable: function() {
            return (this.get('summarylevel') && this.get(SUMLEV_STATE));
        },

        isComplete: function() {
            return !!(this.get('summarylevel') == SUMLEV_NATION || this.get(this.get('summarylevel')));
        },

        shouldShowFilterHelp: function() {
            return this.isFilterable() && !this.filter;
        },

        isFilterable: function() {
            return !!this.get('summarylevel') && !this.isComplete();
        },

        filterDisplay: function() {
            return 'Results matching "' + this.filter + '"';
        },

        location: function() {
            if (!this.get('summarylevel')) return '';

            if (this.get(SUMLEV_TRACT))                     return this.get(SUMLEV_TRACT);
            if (this.get(SUMLEV_PLACE))                     return this.get(SUMLEV_PLACE);
            if (this.get(SUMLEV_COUNTY_SUBDIVISION))        return this.get(SUMLEV_COUNTY_SUBDIVISION);
            if (this.get(SUMLEV_COUNTY))                    return this.get(SUMLEV_COUNTY);
            if (this.get(SUMLEV_STATE))                     return this.get(SUMLEV_STATE);

            return '';
        },

        keydown: function(e) {
            if (e.which == 8) {
                e.preventDefault();
                var _this = window.query;
                _this.filter = _this.filter.substr(0, _this.filter.length - 1);
                _this.lazyRender();
            }
        },

        keypress: function(e) {
            if (e.which == 13) {
                if (this.filter) {
                    $('ol .link:first').trigger('click');
                } else if (this.isCompletable()) {
                    this.go();
                }
            } else if (e.which && this.isFilterable()) {
                this.filter += String.fromCharCode(e.which);
                this.lazyRender();
            }
        },

        filtered: function(list) {
            if (!this.filter) return list;
            var matcher = new RegExp(this.filter.replace(/[-[\]{}()+?.,\\^$|#\s]/ig, "\\$&").replace(/(\\\s)+/, '.*'), 'i');
            return _.filter(list, function(item){ return matcher.test(item[0]); });
        },

        select: function(level, e) {
            this.filter = "";
            var attrs = {};

            //so that we can work backwards up the builder, resetting stuff
            if(level == 'summarylevel' || level == SUMLEV_STATE) {
                delete query.attributes[SUMLEV_NATION];
                delete query.attributes[SUMLEV_COUNTY];
                delete query.attributes[SUMLEV_COUNTY_SUBDIVISION];
                delete query.attributes[SUMLEV_TRACT];
                delete query.attributes[SUMLEV_PLACE];
                delete query.attributes[SUMLEV_BLOCK];
                delete query.attributes[SUMLEV_NATION + 'Display'];
                delete query.attributes[SUMLEV_COUNTY + 'Display'];
                delete query.attributes[SUMLEV_COUNTY_SUBDIVISION + 'Display'];
                delete query.attributes[SUMLEV_TRACT  + 'Display'];
                delete query.attributes[SUMLEV_PLACE  + 'Display'];
                delete query.attributes[SUMLEV_BLOCK  + 'Display'];
                delete query.mappings['places'];
                delete query.mappings['counties'];
                delete query.mappings['counties_subdivisions'];
                delete query.mappings['tracts'];
                //the top level, reset everything
                if(level == 'summarylevel') {
                    delete query.attributes[SUMLEV_STATE];
                    delete query.attributes[SUMLEV_STATE  + 'Display'];
                    delete query.attributes['summarylevelDisplay'];
                }
            }

            var el = $(e.currentTarget);
            var val = attrs[level] = el.attr('data-val');
            var display = attrs[level + 'Display'] = el.text();
            this.currentLevel = level;
            this.set(attrs);
            this.loadNext();

            // Remove this section to enable "go button" prompt:
            var q = window.query;
            if (this.get('summarylevel') && this.get(this.get("summarylevel")))
                // The item we just selected is of the same type as our
                // target datatype. We just picked the value we wanted.
                this.go();
        },

        initializeWithGeography: function(geoid) {
            $.getJSON('/family/' + geoid + '.json', _.bind(function(response) {
                var geographies = response;
                var attrs = {};
                $.each(geographies, function(index,g) {
                    attrs[g.sumlev + "Display"] = g.metadata.NAME;
                    if(geoid == g.geoid) {
                        attrs[SUMLEV_STATE] = g.metadata.STATE;
                        attrs['summarylevel'] = g.sumlev;
                        attrs['summarylevelDisplay'] = query.mappings.summarylevelDisplays[g.sumlev];
                        if(g.sumlev == SUMLEV_TRACT){
                            query.currentLevel = SUMLEV_COUNTY;
                            attrs[SUMLEV_COUNTY] = g.metadata.STATE + g.metadata.COUNTY;
                        } else if (g.sumlev == SUMLEV_COUNTY_SUBDIVISION) {
                            query.currentLevel = SUMLEV_COUNTY_SUBDIVISION;
                            attrs[SUMLEV_COUNTY_SUBDIVISION] = g.metadata.STATE + g.metadata.COUNTY;
                        } else {
                            query.currentLevel = SUMLEV_STATE;
                        }
                    }
                });
                query.set(attrs);
            }, this));
        },

        loadNext: function() {
            var level = this.currentLevel;
            if (level == SUMLEV_STATE) {
                if (_.include([SUMLEV_TRACT, SUMLEV_COUNTY, SUMLEV_COUNTY_SUBDIVISION], this.get('summarylevel'))) {
                    this.loadCounties();
                } else if (this.get('summarylevel') == SUMLEV_PLACE) {
                    this.loadPlaces();
                }
            } else if (level == SUMLEV_COUNTY && this.get('summarylevel') == SUMLEV_COUNTY_SUBDIVISION) {
                this.loadCountySubdivisions();
            } else if (level == SUMLEV_COUNTY && this.get('summarylevel') == SUMLEV_TRACT) {
                this.loadTracts();
            }
        },

        go: function() {
            if (window.location.pathname.indexOf('/data/') != -1 ) {
                //we're on the data page and are adding another
                window.location.pathname = window.location.pathname.replace('.html',',') + this.location() + '.html';
            } else {
                //we're on the homepage
                window.location.pathname = '/data/' + this.location() + '.html';
            }
        },

        csvJson: function() {
            var dataType = '.' + this.innerHTML.toLowerCase()
            var geoid_list = []
            var sumlev = query.attributes.summarylevel
            var containerlev = query.currentLevel
            var container = query.attributes[query.currentLevel]
            window.location = '/internal/download_data_for_region/' +
                sumlev + '-' +
                containerlev + '-'+
                container + dataType;
        },

        showHelp: function(e) {
            $(e.currentTarget).hide();
            $('#help').removeClass('hidden');
        },

        loadCounties: function() {
            $.ajax(API_URL + "/" + this.get(SUMLEV_STATE) + "/counties.jsonp", {
                dataType: "jsonp",
                jsonpCallback: "counties",
                success: _.bind(function(response) {
                    this.mappings.counties = response;
                    this.render();
                }, this)
            });
        },

        loadCountySubdivisions: function() {
            $.ajax(API_URL + "/" + this.get(SUMLEV_STATE) + "/county_subdivisions_" + this.get(SUMLEV_COUNTY) + ".jsonp", {
                dataType: "jsonp",
                jsonpCallback: "county_subdivisions_" + this.get(SUMLEV_COUNTY),
                success: _.bind(function(response) {
                    this.mappings.county_subdivisions = response;
                    this.render();
                }, this)
            });
        },

        loadPlaces: function() {
            $.ajax(API_URL + "/" + this.get(SUMLEV_STATE) + "/places.jsonp", {
                dataType: "jsonp",
                jsonpCallback: "places",
                success: _.bind(function(response) {
                    this.mappings.places = response;
                    this.render();
                }, this)
            });
        },

        loadTracts: function() {
            $.ajax(API_URL + "/" + this.get(SUMLEV_STATE) + "/tracts_" + this.get(SUMLEV_COUNTY) + ".jsonp", {
                dataType: "jsonp",
                jsonpCallback: "tracts_" + this.get(SUMLEV_COUNTY),
                success: _.bind(function(response) {
                    this.mappings.tracts = response;
                    this.render();
                }, this)
            });
        },

        // --------------------- Data ----------------------------------------

        mappings: {

            summarylevels: [SUMLEV_TRACT, SUMLEV_PLACE, SUMLEV_COUNTY, SUMLEV_COUNTY_SUBDIVISION, SUMLEV_STATE, SUMLEV_NATION],

            summarylevelDisplays: {
                //gets filled in during init
            },

            states: []
        }
    });

    var QueryController = Backbone.Controller.extend({

        routes: {
            "query/*query": "loadQuery"
        },

        loadQuery: function(query) {
            // No-op, for now.
        }

    });

    // ------------------------- Initialization -------------------------------

    window.query = new Query;
    query.render();

    query.controller = new QueryController;
    Backbone.history.start();
});
