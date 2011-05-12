{% extends "census/base.sh" %}

{% block install %}
# install some basic stuff
DEBIAN_FRONTEND='noninteractive' \
apt-get -q -y -o Dpkg::Options::='--force-confnew' install \
        zip git-core subversion unattended-upgrades \
        build-essential libxml2-dev libxslt-dev \
        apache2 apache2-mpm-worker apache2-utils apache2.2-common \
        memcached postfix \
        proj libgeoip1 geoip-database python-gdal \
        python-setuptools python-virtualenv python-pip ruby libruby-extras python-dev \
        libapache2-mod-wsgi virtualenvwrapper\
        postgresql-8.4-postgis pgpool libpq-dev

# create postgres user
sudo -u postgres createuser -s $USERNAME

# POSTGIS setup
# Where the postgis templates should be
POSTGIS_SQL_PATH=/usr/share/postgresql/8.4/contrib/postgis-1.5

# Creating the template spatial database.
sudo -u postgres createdb -E UTF8 template_postgis 

# Adding PLPGSQL language support.
sudo -u postgres createlang -d template_postgis plpgsql 

# Allows non-superusers the ability to create from this template
sudo -u postgres psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';" 

# Loading the PostGIS SQL routines
sudo -u postgres psql -d template_postgis -f $POSTGIS_SQL_PATH/postgis.sql 

# Enabling users to alter spatial tables.
sudo -u postgres psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;" 
sudo -u postgres psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"

# some apache config
a2enmod rewrite

# apps dirs
sudo -u $USERNAME \
    mkdir /home/$USERNAME/sites \
          /home/$USERNAME/sites/virtualenvs \
          /home/$USERNAME/apache \
          /home/$USERNAME/logs

# Compatibility
ln -s /home/$USERNAME/apache /home/$USERNAME/sites/apache

# setup virtualenvwrapper
echo "export WORKON_HOME=/home/$USERNAME/sites/virtualenvs" >> /home/$USERNAME/.bashrc

chmod ugo+rw /home/$USERNAME/logs

# install custom configs and scripts
cd $ASSET_DIR/newsapps
cp etc/rsyslog.d/99-newsapps-admin.conf      /etc/rsyslog.d/
cp etc/rsyslog.d/50-default.conf             /etc/rsyslog.d/
cp etc/apache2/apache2.conf                  /etc/apache2/
cp etc/pgpool.conf                           /etc/
cp etc/postgresql/8.4/main/pg_hba.conf       /etc/postgresql/8.4/main/pg_hba.conf
cp etc/postgresql/8.4/main/postgresql.conf   /etc/postgresql/8.4/main/postgresql.conf

# Restart services
service apache2 restart
service postgresql restart
service pgpool restart
service rsyslog restart

{% endblock %}
