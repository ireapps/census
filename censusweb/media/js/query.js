$(function(){
    
    // ------------------------- Constants -----------------------------------
    SUMLEV_NATION = '010';
    SUMLEV_STATE = '040';
    SUMLEV_COUNTY = '050';
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
            $(document.body).keypress(this.keypress);
            document.onkeydown = this.keydown;
            this.bind('change', this.render);
            this.bind('change', this.loadNext);
            this.mappings.summarylevelDisplays[SUMLEV_TRACT] = 'Tracts';
            this.mappings.summarylevelDisplays[SUMLEV_PLACE] = 'Places';
            this.mappings.summarylevelDisplays[SUMLEV_COUNTY] = 'Counties';
            this.mappings.summarylevelDisplays[SUMLEV_STATE] = 'States';
            this.mappings.summarylevelDisplays[SUMLEV_NATION] = 'USA';
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
            $('#place-select .link').click(_.bind(this.select, this, SUMLEV_PLACE));
            $('#tract-select .link').click(_.bind(this.select, this, SUMLEV_TRACT));
            $('.button.go').click(this.go);
            $('.button.csv-json').click(this.csvJson);
            $('.button.remove-column').click(this.remove_column);
            $('tr.row').click(this.twist_row);
            $('.button.show-family').click(this.show_family);
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
            
            if (this.get(SUMLEV_TRACT))         return this.get(SUMLEV_TRACT);
            if (this.get(SUMLEV_PLACE))         return this.get(SUMLEV_PLACE);
            if (this.get(SUMLEV_COUNTY))        return this.get(SUMLEV_COUNTY);
            if (this.get(SUMLEV_STATE))         return this.get(SUMLEV_STATE);

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
                    $('.link:first').trigger('click');
                } else if (this.isCompletable()) {
                    this.go();
                }
            } else if (e.charCode && this.isFilterable()) {
                this.filter += String.fromCharCode(e.charCode);
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
            var el = $(e.currentTarget);
            var val = attrs[level] = el.attr('data-val');
            var display = attrs[level + 'Display'] = el.text();
            this.currentLevel = level;
            this.set(attrs);
            //this.controller.saveLocation('query/' + this.location());
            
            // Remove this section to enable "go button" prompt:
            var q = window.query;
            if (query.get('summarylevel') && query.get(query.get("summarylevel")))
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
                        } else {
                            query.currentLevel = SUMLEV_STATE;
                        }
                    }
                });
                query.set(attrs);
            }, this));
        },

        loadNext: function() {
            console.log(this.currentLevel);
            console.log(this.get('summarylevel'));
            var level = this.currentLevel;
            if (level == SUMLEV_STATE) {
                if (_.include([SUMLEV_TRACT, SUMLEV_COUNTY], this.get('summarylevel'))) {
                    this.loadCounties();
                } else if (this.get('summarylevel') == SUMLEV_PLACE) {
                    this.loadPlaces();
                }
            } else if (level == SUMLEV_COUNTY && this.get('summarylevel') == SUMLEV_TRACT) {
                this.loadTracts();
            }
        },

        go: function() {
            if (window.location.pathname.indexOf('/data/') != -1 ) {
                //we're on the data page and are adding another
                window.location = window.location.href.replace('.html',',') + this.location() + '.html';
            } else {
                //we're on the homepage
                window.location = '/data/' + this.location() + '.html';
            }
        },
        
        csvJson: function() {
            var dataType = '.' + this.innerHTML.toLowerCase()

            var geoid_list = []
            $('.link').each(function() {
                geoid_list.push($(this).attr('data-val'))
            });
            window.location = '/data/' + geoid_list.join(',') + dataType;
        },

        showHelp: function(e) {
            $(e.currentTarget).hide();
            $('#help').removeClass('hidden');
        },

        loadCounties: function() {
            $.getJSON('/internal/counties_for_state/' + this.get(SUMLEV_STATE) + '.json', _.bind(function(response) {
                this.mappings.counties = response;
                this.render();
            }, this));
        },

        loadPlaces: function() {
            $.getJSON('/internal/places_for_state/' + this.get(SUMLEV_STATE) + '.json', _.bind(function(response) {
                this.mappings.places = response;
                this.render();
            }, this));
        },

        loadTracts: function() {
            $.getJSON('/internal/tracts_for_county/' + this.get(SUMLEV_COUNTY) + '.json', _.bind(function(response) {
                this.mappings.tracts = response;
                this.render();
            }, this));
        },
        
        remove_column: function() {
            geoid = $(this).attr('data-val');
            if (document.location.href.indexOf('/' + geoid) > 0) {
                document.location.href = document.location.href.replace(geoid + ',', '');
            } else {
                document.location.href = document.location.href.replace(',' + geoid, '');
            }
        },
        
        twist_row: function() {
            var show_child = !$($('tr[parent=' + $(this).attr('id') + ']')[0]).is(":visible");
            window.query.twist_row_helper($(this), show_child);
            $(this).toggleClass('closed')
            $(this).toggleClass('open');
        },
        
        twist_row_helper: function(parent_row, show_me) {
            $.each($('tr[parent=' + $(parent_row).attr('id') + ']'), function(index, value){
                if(show_me){
                    $(value).show();
                } else {
                    $(value).hide();
                }
                window.query.twist_row_helper(value, false);
            });
        },
        
        show_family: function() {
            geoid = $(this).attr('data-val');
            document.location.href = "/family/" + geoid + "/";
        },
    
        // --------------------- Data ----------------------------------------
    
        mappings: {

            summarylevels: [SUMLEV_TRACT, SUMLEV_PLACE, SUMLEV_COUNTY, SUMLEV_STATE, SUMLEV_NATION],
            
            summarylevelDisplays: {
                //gets filled in during init
            },

            states: [
                ["Alabama"              ,"01"],
                ["Alaska"               ,"02"],
                ["Arizona"              ,"04"],
                ["Arkansas"             ,"05"],
                ["California"           ,"06"],
                ["Colorado"             ,"08"],
                ["Connecticut"          ,"09"],
                ["District of Columbia" ,"11"],
                ["Delaware"             ,"10"],
                ["Florida"              ,"12"],
                ["Georgia"              ,"13"],
                ["Hawaii"               ,"15"],
                ["Iowa"                 ,"19"],
                ["Idaho"                ,"16"],
                ["Illinois"             ,"17"],
                ["Indiana"              ,"18"],
                ["Kansas"               ,"20"],
                ["Kentucky"             ,"21"],
                ["Louisiana"            ,"22"],
                ["Massachusetts"        ,"25"],
                ["Maryland"             ,"24"],
                ["Maine"                ,"23"],
                ["Michigan"             ,"26"],
                ["Minnesota"            ,"27"],
                ["Mississippi"          ,"26"],
                ["Missouri"             ,"29"],
                ["Montana"              ,"29"],
                ["North Carolina"       ,"37"],
                ["North Dakota"         ,"38"],
                ["Nebraska"             ,"31"],
                ["New Hampshire"        ,"33"],
                ["New Jersey"           ,"34"],
                ["New Mexico"           ,"35"],
                ["Nevada"               ,"32"],
                ["New York"             ,"36"],
                ["Ohio"                 ,"39"],
                ["Oklahoma"             ,"40"],
                ["Oregon"               ,"41"],
                ["Pennsylvania"         ,"42"],
                ["Rhode Island"         ,"44"],
                ["South Carolina"       ,"45"],
                ["South Dakota"         ,"46"],
                ["Tennessee"            ,"47"],
                ["Texas"                ,"48"],
                ["Utah"                 ,"49"],
                ["Virginia"             ,"78"],
                ["Vermont"              ,"50"],
                ["Washington"           ,"53"],
                ["Wisconsin"            ,"55"],
                ["West Virginia"        ,"54"],
                ["Wyoming"              ,"56"]
            ]
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

    // Table mouseover row highlighting.
    $(".report tr").hover(function() {
        $(this).addClass("highlight");
    }, function() {
        $(this).removeClass('highlight');
    });
    
});
