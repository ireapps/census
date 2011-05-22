$(function(){
    $(document).ready(function() {
        reportcontroller = new ReportController
        Backbone.history.start()
    })

    ReportController = Backbone.Controller.extend({
        routes: {
            "browser": "browser"
        },

        browser: function() {
            b = new Browser
        }
    })

    Browser = Backbone.View.extend({
        tagName: "aside",
        id: "browser",
        events: {},

        initialize: function() {
            this.template = _.template($('#browser-template').html())

            $.getJSON('/labels/2010.json', _.bind(function(response) {
                this.model = new Backbone.Model(response)
                this.render()
            }, this))

            _.bindAll(this)

            $('#container').before(this.el)
        },

        render: function() {
            $(this.el).html(this.template({model:this.model}))
            $(this.el).find('#table-list').tree({default_expanded_paths_string : '0/0/0,0/0/2,0/2/4'})
            return this
        }

    })


})
