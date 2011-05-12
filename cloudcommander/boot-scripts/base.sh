#!/bin/bash
{% block start %}
USERNAME=ubuntu
{% endblock %}

# Make sure we have a locale defined
export LANG="en_US.UTF-8"

{% if server.name -%}
# configure hostname
echo {{ server.name }} > /etc/hostname
hostname {{ server.name }}
{% endif -%}

# update the software
export DEBIAN_FRONTEND=noninteractive
apt-get -q update && apt-get -q upgrade -y

apt-get install python-setuptools

# need an updated version of boto
easy_install --upgrade boto

# Carry over AWS keys for s3cmd
echo "[default]
access_key = {{settings.access_key}}
secret_key = {{settings.secret_key}}" > /home/$USERNAME/.s3cfg

# Setup profile stuff
echo "export SECURITY_GROUP={{settings.security_group}}
export PRIVATE_KEY=/home/$USERNAME/.ssh/{{settings.key_pair}}.pem
export AWS_ACCESS_KEY_ID={{settings.access_key}}
export AWS_SECRET_ACCESS_KEY={{settings.secret_key}}
{% if server.cluster -%}
export CLUSTER={{server.cluster}}
{% endif -%}
" > /etc/profile.d/cloud-commander.sh
source /etc/profile

# install s3cmd
apt-get -q install s3cmd

# Pull down assets
ASSET_DIR="/home/$USERNAME/cloud-commander"
s3cmd get --config=/home/$USERNAME/.s3cfg --no-progress s3://{{settings.asset_bucket}}/{{settings.cc_key}}-assets.tgz /home/$USERNAME/assets.tgz

cd /home/$USERNAME 
tar -zxf assets.tgz

# fix asset permissions
chown -Rf root:root $ASSET_DIR
chmod -Rf 755 $ASSET_DIR

# install scripts
if [ -d $ASSET_DIR/bin ]; then
    if [ ! -d /usr/local/bin ]; then
        mkdir /usr/local/bin
    fi
    cp $ASSET_DIR/bin/* /usr/local/bin
fi

# load private keys
cp $ASSET_DIR/*.pem /home/$USERNAME/.ssh/

# load authorized keys
if [ -f $ASSET_DIR/authorized_keys ]; then
    cat $ASSET_DIR/authorized_keys >> /home/$USERNAME/.ssh/authorized_keys
fi

# load known hosts
if [ -f $ASSET_DIR/known_hosts ]; then
    cp $ASSET_DIR/known_hosts /home/$USERNAME/.ssh/known_hosts
fi

# fix permissions in ssh folder
chmod -Rf go-rwx /home/$USERNAME/.ssh

# setup private key to be used by default for ssh connections
echo "IdentityFile /home/$USERNAME/.ssh/{{settings.key_pair}}.pem" > /home/$USERNAME/.ssh/config

# setup our local hosts file
/usr/local/bin/hosts-for-cluster

{% block install %}

{% endblock %}

# Fix any perms that might have gotten messed up
chown -Rf $USERNAME:$USERNAME /home/$USERNAME

# Update CC status - remove instance booting semaphore from s3
s3cmd del --config=/home/$USERNAME/.s3cfg {{settings.assets_s3_url}}`ec2metadata --instance-id`._cc_

{% block finish %}{% endblock %}

