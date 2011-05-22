# Chicago Tribune News Applications fabfile
# No copying allowed

from fabric.api import *

"""
Base configuration
"""
#name of the deployed site if different from the name of the project
env.site_name = 'censusweb'

env.project_name = 'censusweb'
env.database_password = 'Xy9XKembdu'
env.site_media_prefix = "site_media"
env.admin_media_prefix = "admin_media"
env.path = '/home/ubuntu/sites/%(project_name)s' % env
env.log_path = '/home/ubuntu/logs' % env
env.env_path = '/home/ubuntu/sites/virtualenvs/%(project_name)s' % env
env.repo_path = '%(path)s' % env
env.site_path = '%(repo_path)s/censusweb' % env
env.dataprocessing_path = '%(repo_path)s/dataprocessing' % env
env.apache_config_path = '/home/ubuntu/apache/%(project_name)s' % env
env.python = 'python2.6'
env.repository_url = "git@github.com:documentcloud/census.git"
env.memcached_server_address = "cache"
env.cache_server = "lb"
env.multi_server = False

"""
Environments
"""
def production():
    """
    Work on production environment
    """
    #TKTK
    env.settings = 'production'
    env.hosts = ['db.censusweb.ire.org']
    env.user = 'ubuntu'
    env.s3_bucket = 'media.censusweb.ire.org'
    env.site_domain = 'censusweb.censusweb.ire.org'    

def staging():
    """
    Work on staging environment
    """
    env.settings = 'staging'
    env.hosts = ['censusweb.beta.tribapps.com'] 
    env.user = 'ubuntu'
    env.s3_bucket = 'media-beta.tribapps.com'
    env.site_domain = 'censusweb.beta.tribapps.com'    
    
"""
Branches
"""
def stable():
    """
    Work on stable branch.
    """
    env.branch = 'stable'

def master():
    """
    Work on development branch.
    """
    env.branch = 'master'

def branch(branch_name):
    """
    Work on any specified branch.
    """
    env.branch = branch_name
    
"""
Commands - setup
"""
def setup():
    """
    Setup a fresh virtualenv, install everything we need, and fire up the database.
    
    Does NOT perform the functions of deploy().
    """
    require('settings', provided_by=[production, staging])
    require('branch', provided_by=[stable, master, branch])
    
    setup_directories()
    setup_virtualenv()
    clone_repo()
    checkout_latest()
    install_requirements()
    destroy_database()
    create_database()
    load_data()
    install_apache_conf()
    deploy_requirements_to_s3()

def setup_directories():
    """
    Create directories necessary for deployment.
    """
    run('mkdir -p %(path)s' % env)
    
def setup_virtualenv():
    """
    Setup a fresh virtualenv.
    """
    run('virtualenv -p %(python)s --no-site-packages %(env_path)s;' % env)
    run('source %(env_path)s/bin/activate; easy_install -U setuptools; easy_install -U pip;' % env)

def clone_repo():
    """
    Do initial clone of the git repository.
    """
    run('git clone %(repository_url)s %(repo_path)s' % env)

def checkout_latest():
    """
    Pull the latest code on the specified branch.
    """
    run('cd %(repo_path)s; git checkout %(branch)s; git pull origin %(branch)s' % env)

def install_requirements():
    """
    Install the required packages using pip.
    """
    run('source %(env_path)s/bin/activate; pip install -q -r %(site_path)s/requirements.txt' % env)

def install_apache_conf():
    """
    Install the apache site config file.
    """
    sudo('cp %(site_path)s/config/%(settings)s/apache %(apache_config_path)s' % env)

def deploy_requirements_to_s3():
    """
    Deploy the admin media to s3.
    """
    with settings(warn_only=True):
        run('s3cmd del --recursive s3://%(s3_bucket)s/%(project_name)s/%(admin_media_prefix)s/' % env)
    run('s3cmd -P --guess-mime-type --rexclude-from=%(site_path)s/s3exclude sync %(env_path)s/src/django/django/contrib/admin/media/ s3://%(s3_bucket)s/%(project_name)s/%(admin_media_prefix)s/' % env)


"""
Commands - deployment
"""
def deploy():
    """
    Deploy the latest version of the site to the server and restart Apache2.
    
    Does not perform the functions of load_new_data().
    """
    require('settings', provided_by=[production, staging])
    require('branch', provided_by=[stable, master, branch])
    
    with settings(warn_only=True):
        maintenance_up()
        
    checkout_latest()
    gzip_assets()
    deploy_to_s3()
    maintenance_down()
    
def maintenance_up():
    """
    Install the Apache maintenance configuration.
    """
    sudo('cp %(site_path)s/config/%(settings)s/apache_maintenance %(apache_config_path)s' % env)
    reboot()

def gzip_assets():
    """
    GZips every file in the media directory and places the new file
    in the gzip directory with the same filename.
    """
    run('cd %(site_path)s; python gzip_assets.py' % env)

def deploy_to_s3():
    """
    Deploy the latest project site media to S3.
    """
    env.media_path = '%(site_path)s/media/' % env
    run(('s3cmd -P --guess-mime-type --rexclude-from=%(site_path)s/s3exclude sync %(media_path)s s3://%(s3_bucket)s/%(project_name)s/%(site_media_prefix)s/') % env)

    env.gzip_path = '%(site_path)s/gzip_media/' % env
    run(('s3cmd -P --add-header=Content-encoding:gzip --guess-mime-type --rexclude-from=%(site_path)s/s3exclude sync %(gzip_path)s s3://%(s3_bucket)s/%(project_name)s/%(site_media_prefix)s/') % env)
       
def reboot(): 
    """
    Restart the Apache2 server.
    """
    if env.multi_server:
        run('bounce-apaches-for-cluster')
    else:
        sudo('service apache2 restart')
    
def maintenance_down():
    """
    Reinstall the normal site configuration.
    """
    install_apache_conf()
    reboot()
    
"""
Commands - rollback
"""
def rollback(commit_id):
    """
    Rolls back to specified git commit hash or tag.
    
    There is NO guarantee we have committed a valid dataset for an arbitrary
    commit hash.
    """
    require('settings', provided_by=[production, staging])
    require('branch', provided_by=[stable, master, branch])
    
    maintenance_up()
    checkout_latest()
    git_reset(commit_id)
    gzip_assets()
    deploy_to_s3()
    maintenance_down()
    
def git_reset(commit_id):
    """
    Reset the git repository to an arbitrary commit hash or tag.
    """
    env.commit_id = commit_id
    run("cd %(repo_path)s; git reset --hard %(commit_id)s" % env)

"""
Commands - data
"""
def load_new_data():
    """
    Erase the current database and load new data from the SQL dump file.
    """
    require('settings', provided_by=[production, staging])
    
    maintenance_up()
    pgpool_down()
    destroy_database()
    create_database()
    load_data()
    pgpool_up()
    maintenance_down()
    
def create_database(func=run):
    """
    Creates the user and database for this project.
    """
    func('createuser -s %(project_name)s' % env)
    func('echo "ALTER USER %(project_name)s with password %(database_password)s" | psql postgres' % env)
    func('echo "GRANT ALL PRIVILEGES TO %(project_name)s;" | psql postgres' % env)
    func('createdb -O %(project_name)s %(project_name)s -T template_postgis' % env)
    
def destroy_database(func=run):
    """
    Destroys the user and database for this project.
    
    Will not cause the fab to fail if they do not exist.
    """
    with settings(warn_only=True):
        func('dropdb %(project_name)s' % env)
        func('dropuser %(project_name)s' % env)
        
def load_data():
    """
    Loads data from the repository into PostgreSQL.
    """
    run('psql -q %(project_name)s < %(site_path)s/data/psql/dump.sql' % env)
    
def pgpool_down():
    """
    Stop pgpool so that it won't prevent the database from being rebuilt.
    """
    sudo('/etc/init.d/pgpool stop')
    
def pgpool_up():
    """
    Start pgpool.
    """
    sudo('/etc/init.d/pgpool start')

"""
Commands - Data Processing
"""
def batch_sf_2000(state, fake=''):
    """
    Kick off the SF 2000 data loader for a state.
    """
    command = './batch_sf_2000.sh %s %s' % (state, fake)
    loader_log = '%s/census.load.%s.log' % (env.log_path, state)
    run("touch %s" % loader_log)

    with cd(env.dataprocessing_path):
        run("source %s/bin/activate; nohup %s >& %s < /dev/null &" % (env.env_path, command, loader_log))

def batch_sf_2010(state, fake=''):
    """
    Kick off the SF 2010 data loader for a state.
    """
    command = './batch_sf_2010.sh %s %s' % (state, fake)
    loader_log = '%s/census.load.%s.log' % (env.log_path, state)
    run("touch %s" % loader_log)

    with cd(env.dataprocessing_path):
        run("source %s/bin/activate; nohup %s >& %s < /dev/null &" % (env.env_path, command, loader_log))

"""
Commands - miscellaneous
"""
    
def clear_cache():
    """
    Restart memcache, wiping the current cache.
    """
    if env.multi_server:
        run('bounce-memcaches-for-cluster')
    else:
        sudo('service memcached restart')

    run('curl -X PURGE -H "Host: %(site_domain)s" http://%(cache_server)s/' % env)
    
def echo_host():
    """
    Echo the current host to the command line.
    """
    run('echo %(settings)s; echo %(hosts)s' % env)

"""
Deaths, destroyers of worlds
"""
def shiva_the_destroyer():
    """
    Remove all directories, databases, etc. associated with the application.
    """
    with settings(warn_only=True):
        run('rm -Rf %(path)s' % env)
        run('rm -Rf %(env_path)s' % env)
        pgpool_down()
        run('dropdb %(project_name)s' % env)
        run('dropuser %(project_name)s' % env)
        pgpool_up()
        sudo('rm %(apache_config_path)s' % env)
        reboot()
        run('s3cmd del --recursive s3://%(s3_bucket)s/%(project_name)s' % env)

def local_shiva():
    destroy_database(local)

def local_bootstrap():
    create_database(local)

    # Normal bootstrap
    # local('python manage.py syncdb --noinput')
    local('psql censusweb < data/psql/dump.sql')
    # Bootstrap with south
    # local('python manage.py syncdb --all --noinput')
    # local('python manage.py migrate --fake')

"""
Utility functions (not to be called directly)
"""
def _execute_psql(query):
    """
    Executes a PostgreSQL command using the command line interface.
    """
    env.query = query
    run(('cd %(site_path)s; psql -q %(project_name)s -c "%(query)s"') % env)
    
def _confirm_branch():
    if (env.settings == 'production' and env.branch != 'stable'):
        answer = prompt("You are trying to deploy the '%(branch)s' branch to production.\nYou should really only deploy a stable branch.\nDo you know what you're doing?" % env, default="Not at all")
        if answer not in ('y','Y','yes','Yes','buzz off','screw you'):
            exit()
