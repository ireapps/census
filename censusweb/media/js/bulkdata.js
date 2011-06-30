$(function(){
    window.init_bulk_data = function() {
        availableStates(function(states) {
            _(states).each(function(s) { $("#state-download").append("<option value='"+ s + "'>" + s + "</option");});
        })
    };
    
    init_bulk_data();
});
