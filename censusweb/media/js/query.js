$(function(){

    // ------------------------- Query Model ---------------------------------

    window.Query = function(){
        _.bindAll(this, 'selectSummaryLevel', 'selectState', 'selectCounty',
                        'selectPlace');
        this.template = _.template($('#query-template').html());
    };

    Query.prototype.render = function() {
        $("#search").html(this.template({query: this}));
        $('#filter-help').toggle(!!this.summarylevel);
        $("#summarylevel-select .link").click(this.selectSummaryLevel);
        $("#state-select .link").click(this.selectState);
        $('#county-select .link').click(this.selectCounty);
        $('#place-select .link').click(this.selectPlace);
    };

    Query.prototype.isComplete = function() {
        return (this.summarylevel && this.state);
    };

    Query.prototype.selectSummaryLevel = function(e) {
        var el = $(e.currentTarget);
        this.summarylevel = el.attr('data-val');
        this.summarylevelDisplay = el.text();
        this.render();
    };

    Query.prototype.selectState = function(e) {
        var el = $(e.currentTarget);
        this.state = el.attr('data-val');
        this.stateDisplay = el.text();
        this.render();
        if (this.summarylevel == 'tract' || this.summarylevel == 'county') {
            this.loadCounties();
        } else if (this.summarylevel == 'place') {
            this.loadPlaces();
        }
    };

    Query.prototype.selectCounty = function(e) {
        var el = $(e.currentTarget);
        this.county = el.attr('data-val');
        this.countyDisplay = el.text();
        this.render();
    };

    Query.prototype.selectPlace = function(e) {
        var el = $(e.currentTarget);
        this.place = el.attr('data-val');
        this.placeDisplay = el.text();
        this.render();
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

    // ------------------------- Data ---------------------------------

    Query.prototype.mappings = {
        states: [
            ["AK", "Alaska"],
	        ["AL", "Alabama"],
	        ["AR", "Arkansas"],
	        ["AZ", "Arizona"],
	        ["CA", "California"],
	        ["CO", "Colorado"],
	        ["CT", "Connecticut"],
	        ["DC", "District of Columbia"],
	        ["DE", "Delaware"],
	        ["FL", "Florida"],
	        ["GA", "Georgia"],
	        ["HI", "Hawaii"],
	        ["IA", "Iowa"],
	        ["ID", "Idaho"],
	        ["IL", "Illinois"],
	        ["IN", "Indiana"],
	        ["KS", "Kansas"],
	        ["KY", "Kentucky"],
	        ["LA", "Louisiana"],
	        ["MA", "Massachusetts"],
	        ["MD", "Maryland"],
	        ["ME", "Maine"],
	        ["MI", "Michigan"],
	        ["MN", "Minnesota"],
	        ["MO", "Missouri"],
	        ["MS", "Mississippi"],
	        ["MT", "Montana"],
	        ["NC", "North Carolina"],
	        ["ND", "North Dakota"],
	        ["NE", "Nebraska"],
	        ["NH", "New Hampshire"],
	        ["NJ", "New Jersey"],
	        ["NM", "New Mexico"],
	        ["NV", "Nevada"],
	        ["NY", "New York"],
	        ["OH", "Ohio"],
	        ["OK", "Oklahoma"],
	        ["OR", "Oregon"],
	        ["PA", "Pennsylvania"],
	        ["RI", "Rhode Island"],
	        ["SC", "South Carolina"],
	        ["SD", "South Dakota"],
	        ["TN", "Tennessee"],
	        ["TX", "Texas"],
	        ["UT", "Utah"],
	        ["VA", "Virginia"],
	        ["VT", "Vermont"],
	        ["WA", "Washington"],
	        ["WI", "Wisconsin"],
	        ["WV", "West Virginia"],
	        ["WY", "Wyoming"]
        ]
    };

    // ------------------------- Initialization -------------------------------

    var query = new Query;
    query.render();

});