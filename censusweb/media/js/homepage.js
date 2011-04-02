$(function(){

    var countyTemplate = _.template($('#county-select-template').html());

    // When a state is selected, grab and render the list of counties.
    $('#state-select').change(function() {
        var stateCode = $(this).val();
        if (stateCode) {
            $.getJSON('/internal/counties_for_state/' + stateCode + '.json', function(response) {
                var html = countyTemplate({counties: response});
                $('#county-select-wrap').show().html(html);
            });
        } else {
            $('#county-select-wrap').hide();
        }
    });

});