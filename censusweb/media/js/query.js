$(function(){

    // ------------------------- Query Model ---------------------------------

    window.Query = function(){
        _.bindAll(this, 'keypress', 'render', 'showHelp');
        this.template = _.template($('#query-template').html());
        this.lazyRender = _.debounce(this.render, 50);
        this.filter = '';
        $(document.body).keypress(this.keypress);
    };

    Query.prototype.render = function() {
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
    };

    Query.prototype.isCompletable = function() {
        return (this.summarylevel && this.state);
    };

    Query.prototype.isComplete = function() {
        return this.summarylevel == 'nation' || this[this.summarylevel];
    };

    Query.prototype.shouldShowFilterHelp = function() {
        return this.isFilterable() && !this.filter;
    };

    Query.prototype.isFilterable = function() {
        return !!this.summarylevel && !this.isComplete();
    };

    Query.prototype.filterDisplay = function() {
        return 'Results matching "' + this.filter + '"';
    };

    Query.prototype.keypress = function(e) {
        if (e.which == 8) {
            this.filter = this.filter.substr(0, this.filter.length - 1);
            this.lazyRender();
        } else if (e.which == 13 && this.filter) {
            $('.link:first').trigger('click');
        } else if (e.charCode && this.isFilterable()) {
            this.filter += String.fromCharCode(e.charCode);
            this.lazyRender();
        }
    };

    Query.prototype.filtered = function(list) {
        if (!this.filter) return list;
        var matcher = new RegExp(this.filter.replace(/[-[\]{}()+?.,\\^$|#\s]/ig, "\\$&").replace(/(\\\s)+/, '.*'), 'i');
        return _.filter(list, function(item){ return matcher.test(item[0]); });
    };

    Query.prototype.select = function(level, e) {
        this.filter = "";
        var el = $(e.currentTarget);
        var val = this[level] = el.attr('data-val');
        var display = this[level + 'Display'] = el.text();
        this.render();
        if (this.isComplete()) return this.finish();
        if (level == 'state') {
            if (this.summarylevel == 'tract' || this.summarylevel == 'county' || this.summarylevel == 'subdivision') {
                this.loadCounties();
            } else if (this.summarylevel == 'place') {
                this.loadPlaces();
            }
        } else if (level == 'county' && this.summarylevel == 'subdivision') {
            this.loadSubdivisions();
        } else if (level == 'county' && this.summarylevel == 'tract') {
            this.loadTracts();
        }
    };

    Query.prototype.finish = function() {
        switch (this.summarylevel) {
            case "tract":
                window.location = '/tracts/' + this.state + '/' + this.county.substr(2) + '/' + this.tract + '.html';
                break;
        }
    };

    Query.prototype.showHelp = function(e) {
        $(e.currentTarget).hide();
        $('#help').removeClass('hidden');
    };

    Query.prototype.loadCounties = function() {
        $.getJSON('/internal/counties_for_state/' + this.state + '.json', _.bind(function(response) {
            this.mappings.counties = response;
            this.render();
        }, this));
    };

    Query.prototype.loadPlaces = function() {
        $.getJSON('/internal/places_for_state/' + this.state + '.json', _.bind(function(response) {
            this.mappings.places = response;
            this.render();
        }, this));
    };

    Query.prototype.loadSubdivisions = function() {
        $.getJSON('/internal/subdivisions_for_county/' + this.county + '.json', _.bind(function(response) {
            this.mappings.subdivisions = response;
            this.render();
        }, this));
    };

    Query.prototype.loadTracts = function() {
        $.getJSON('/internal/tracts_for_county/' + this.county + '.json', _.bind(function(response) {
            this.mappings.tracts = response;
            this.render();
        }, this));
    };

    // ------------------------- Data ---------------------------------

    Query.prototype.mappings = {

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
    };

    // ------------------------- Initialization -------------------------------

    window.query = new Query;
    query.render();

});