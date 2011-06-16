census.ire.org
==============

A nationwide census browser for 2000 and 2010 census data.

Dependencies
============

You will need Python 2.7, the PostGIS stack, virtualenv and virtualenvwrapper. Mac Installation instructions at: http://blog.apps.chicagotribune.com/2010/02/17/quick-install-pythonpostgis-geo-stack-on-snow-leopard/):

Other required software:

* mongodb
* wget
* mdbtools.

On a Mac you can get these with Brew::

    brew install mongodb
    brew install wget
    brew install mdbtools

Bootstrapping the webapp
========================

To get the web application running::

    cd censusweb
    mkvirtualenv --no-site-packages censusweb
    pip install -r requirements.txt
    python manage.py runserver

Configuring the webapp
======================

By default the webapp is going to use the data published to the IRE test site, which may not be accessible to you. To use your own data open censusweb/config/settings.py and modify the following line::

    API_URL = 'http://s3.amazonaws.com/census-test' 

See the next section to learn how to deploy data to your custom S3 bucket.

Loading data
============

Once you've setup the webapp you will have the requirements needed to load data. If you want to load embargoed data you will need to define environment variables for your username and password::

    CENSUS_USER=cgroskopf@tribune.com
    CENSUS_PASS=NotMyRealPassword

You will also need to have defined your Amazon Web Services credentials so that you can upload the rendered data files to S3::

    export AWS_ACCESS_KEY_ID="foo"
    export AWS_SECRET_ACCESS_KEY="bar"

You will also need to modify the load configuration to point at the same S3 bucket you configured for the webapp. Open dataprocessing/config.py and modify the following lines::

    S3_BUCKETS = {
        'staging': 'census-test',
        'production': 'censusdata.ire.org',
    } 

To load SF1 data for Hawaii make sure you have Mongo running and then execute the following commands::

    cd dataprocessing
    ./batch_sf.sh Hawaii staging

Credits
=======

This application was a project of `Investigative Reporters and Editors (IRE) <http://www.ire.org/>`_ / `National Institute for Computer-Assisted Reporting (NICAR) <http://data.nicar.org/>`_. Funding was generously provided by `The Reynolds Journalism Institute <http://www.rjionline.org/>`_

The following journolists and nerds contributed to this project:

* Jeremy Ashkenas (DocumentCloud)
* Brian Boyer (Chicago Tribune)
* Christopher Groskopf (Chicago Tribune)
* Joe Germuska (Chicago Tribune)
* Mark Horvit (IRE)
* Ryan Mark (Chicago Tribune)
* Curt Merrill (CNN)
* Paul Overberg (USA Today)
* Ted Peterson (IRE)
* Aron Pilhofer (New York Times)
* Mike Tigas (Spokesman-Review)
* Matt Waite (University of Nebraska)

License
=======

This software is licensed under the permissive MIT license. See COPYING for details.
