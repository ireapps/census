$(function(){

    // ------------------------- Query Model ---------------------------------

    window.Query = function(){
        _.bindAll(this, 'selectSummaryLevel', 'selectState', 'selectCounty');
        this.template = _.template($('#query-template').html());
    };

    Query.prototype.render = function() {
        $("#search").html(this.template({query: this}));
        $("#summarylevel-select .link").click(this.selectSummaryLevel);
        $("#state-select .link").click(this.selectState);
        $('#county-select .link').click(this.selectCounty);
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
        this.loadCounties();
    };

    Query.prototype.selectCounty = function(e) {
        var el = $(e.currentTarget);
        this.county = el.attr('data-val');
        this.countyDisplay = el.text();
        this.render();
    };

    Query.prototype.loadCounties = function() {
        $.getJSON('/internal/counties_for_state/' + this.state + '.json', _.bind(function(response) {
            this.counties = response;
            this.render();
        }, this));
    };

    var query = new Query;
    query.render();

    // ------------------------- Data ---------------------------------

    Query.mappings = {
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

});