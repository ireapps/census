$(function(){

    // ------------------------- Query Model ---------------------------------

    window.Query = Backbone.Model.extend({

        initialize: function() {
            _.bindAll(this, 'keypress', 'render', 'showHelp');
            this.template = _.template($('#query-template').html());
            this.lazyRender = _.debounce(this.render, 50);
            this.filter = '';
            $(document.body).keypress(this.keypress);
        },

        render: function() {
            $("#search").html(this.template({query: this}));
            $('#filter-help').toggle(!!this.shouldShowFilterHelp());
            $('#filter-display').toggle(!!this.filter).text(this.filterDisplay());
            $('#help-link').click(this.showHelp);
            $("#summarylevel-select .link").click(_.bind(this.select, this, 'summarylevel'));
            $("#state-select .link").click(_.bind(this.select, this, 'state'));
            $('#county-select .link').click(_.bind(this.select, this, 'county'));
            $('#place-select .link').click(_.bind(this.select, this, 'place'));
            $('#subdivision-select .link').click(_.bind(this.select, this, 'subdivision'));
            $('#tract-select .link').click(_.bind(this.select, this, 'tract'));
        },

        isCompletable: function() {
            return (this.get('summarylevel') && this.get('state'));
        },

        isComplete: function() {
            return !!(this.get('summarylevel') == 'nation' || this.get(this.get('summarylevel')));
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
            var parts = [this.get('summarylevel')];
            if (this.get('state'))         parts.push(this.get('state'));
            if (this.get('county'))        parts.push(this.get('county').substr(2));
            if (this.get('subdivision'))   parts.push(this.get('subdivision'));
            if (this.get('place'))         parts.push(this.get('place'));
            if (this.get('tract'))         parts.push(this.get('tract'));
            return parts.join('-');
        },

        keypress: function(e) {
            if (e.which == 8) {
                e.preventDefault();
                this.filter = this.filter.substr(0, this.filter.length - 1);
                this.lazyRender();
            } else if (e.which == 13 && this.filter) {
                $('.link:first').trigger('click');
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
            this.controller.saveLocation('query/' + this.location());
            this.set(attrs);
            this.render();
            if (this.isComplete()) return this.finish();
            if (level == 'state') {
                if (_.include(['tract', 'county', 'subdivision'], this.get('summarylevel'))) {
                    this.loadCounties();
                } else if (this.get('summarylevel') == 'place') {
                    this.loadPlaces();
                }
            } else if (level == 'county' && this.get('summarylevel') == 'subdivision') {
                this.loadSubdivisions();
            } else if (level == 'county' && this.get('summarylevel') == 'tract') {
                this.loadTracts();
            }
        },

        finish: function() {
            window.location = '/data/' + this.location() + '.html';
        },

        showHelp: function(e) {
            $(e.currentTarget).hide();
            $('#help').removeClass('hidden');
        },

        loadCounties: function() {
            $.getJSON('/internal/counties_for_state/' + this.get('state') + '.json', _.bind(function(response) {
                this.mappings.counties = response;
                this.render();
            }, this));
        },

        loadPlaces: function() {
            $.getJSON('/internal/places_for_state/' + this.get('state') + '.json', _.bind(function(response) {
                this.mappings.places = response;
                this.render();
            }, this));
        },

        loadSubdivisions: function() {
            $.getJSON('/internal/subdivisions_for_county/' + this.get('county') + '.json', _.bind(function(response) {
                this.mappings.subdivisions = response;
                this.render();
            }, this));
        },

        loadTracts: function() {
            $.getJSON('/internal/tracts_for_county/' + this.get('county') + '.json', _.bind(function(response) {
                this.mappings.tracts = response;
                this.render();
            }, this));
        },

        // ------------------------- Data ---------------------------------

        mappings: {

            summarylevels: ['tract', 'place', 'subdivision', 'county', 'state', 'nation'],

            states: [
                ["Alabama"              ,"AL"],
                ["Alaska"               ,"AK"],
	            ["Arizona"              ,"AZ"],
	            ["Arkansas"             ,"AR"],
	            ["California"           ,"CA"],
	            ["Colorado"             ,"CO"],
	            ["Connecticut"          ,"CT"],
	            ["District of Columbia" ,"DC"],
	            ["Delaware"             ,"DE"],
	            ["Florida"              ,"FL"],
	            ["Georgia"              ,"GA"],
	            ["Hawaii"               ,"HI"],
	            ["Iowa"                 ,"IA"],
	            ["Idaho"                ,"ID"],
	            ["Illinois"             ,"IL"],
	            ["Indiana"              ,"IN"],
	            ["Kansas"               ,"KS"],
	            ["Kentucky"             ,"KY"],
	            ["Louisiana"            ,"LA"],
	            ["Massachusetts"        ,"MA"],
	            ["Maryland"             ,"MD"],
	            ["Maine"                ,"ME"],
	            ["Michigan"             ,"MI"],
	            ["Minnesota"            ,"MN"],
	            ["Mississippi"          ,"MS"],
	            ["Missouri"             ,"MO"],
	            ["Montana"              ,"MT"],
	            ["North Carolina"       ,"NC"],
	            ["North Dakota"         ,"ND"],
	            ["Nebraska"             ,"NE"],
	            ["New Hampshire"        ,"NH"],
	            ["New Jersey"           ,"NJ"],
	            ["New Mexico"           ,"NM"],
	            ["Nevada"               ,"NV"],
	            ["New York"             ,"NY"],
	            ["Ohio"                 ,"OH"],
	            ["Oklahoma"             ,"OK"],
	            ["Oregon"               ,"OR"],
	            ["Pennsylvania"         ,"PA"],
	            ["Rhode Island"         ,"RI"],
	            ["South Carolina"       ,"SC"],
	            ["South Dakota"         ,"SD"],
	            ["Tennessee"            ,"TN"],
	            ["Texas"                ,"TX"],
	            ["Utah"                 ,"UT"],
	            ["Virginia"             ,"VA"],
	            ["Vermont"              ,"VT"],
	            ["Washington"           ,"WA"],
	            ["Wisconsin"            ,"WI"],
	            ["West Virginia"        ,"WV"],
	            ["Wyoming"              ,"WY"]
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

});