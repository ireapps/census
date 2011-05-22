$(function(){
    $(document).ready(function() {
        reportcontroller = new ReportController
        Backbone.history.start()
        if ( !location.hash )
            location.hash="#browser"
    })

    ReportController = Backbone.Controller.extend({
        routes: {
            "browser": "browser",
            "browser/:set": "browser"
        },

        browser: function(set) {
            // set is a comma list of table ids to show
            if ( set ) {
                var show_ids = set.split(',')
            } else if($.cookie('show_tables')) {
                this.saveLocation("browser/"+$.cookie('show_tables'))
                var show_ids = $.cookie('show_tables').split(',')
            } else {
                var show_ids = ['H1']
            }

            $("table.report").hide()
            _.each(show_ids, function(id) {
                $('#report-'+id).show()
            })

            if ( ! this.browser_view ) {
                var m = new Backbone.Model({'table_ids': show_ids})
                this.browser_view = new Browser({model: m})
            }
        }
    })

    Browser = Backbone.View.extend({
        tagName: "aside",
        id: "browser",
        events: {
            "change input": "check",
            "click .link": "scroll"
        },

        initialize: function() {
            this.template = _.template($('#browser-template').html())

            _.bindAll(this)

            this.model.bind('change', function(model) {
                var table_ids = model.get('table_ids').join(',')
                $.cookie('show_tables', table_ids)
                window.location.hash = "#browser/"+table_ids 
            })

            this.render()

            $('#container').before(this.el)
        },

        render: function() {
            $(this.el).html(this.template({model:this.model}))
            $(this.el).find('#table-list').tree({default_expanded_paths_string : '0/0/0,0/0/2,0/2/4'})
            return this
        },

        check: function(ev) {
            var id = $(ev.target).attr('id').match(/^show-report-(.+)$/)[1]
            var table_ids = this.model.get('table_ids')

            if ( $(ev.target).is(':checked') ) {
                this.model.set({'table_ids': table_ids.concat([id])})
            } else {
                this.model.set({'table_ids': _.without(table_ids, id)})
            }
        },

        scroll: function(ev) {
            var a_name = $(ev.target).attr('href').match(/^#(.*)$/)[1]
            $("html").scrollTop($("a[name="+a_name+"]").offset().top)

            return false
        }

    })


})
