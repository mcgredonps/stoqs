## PyDap

PyDap is a system for serving up netcdf files remotely.

Instructions for installing PyDap with Apache are here:

http://www.pydap.org/server.html#running-pydap-with-apache

Assuming a standard apache install, with the standard HTML content
in /var/www/html and the configuration file in /etc/httpd/conf, installing
it goes something like this:

# Create a pydap directory outside the standard content directory.
# The virualenv.py file creates a virtual environment directory with the 
# necessary python supporting packages. Pip will place the supporting
# packages there.

mkdir /var/www/pydap
python /usr/local/lib/python2.7/site-packages/virtualenv.py /var/www/pydap/env

# Create the virual environment
 python virtualenv.py --system-site-packages /var/www/pydap/env

# Source the file necessary to set the environment variables. 
source /var/www/pydap/env/bin/activate
pip install Pydap

# Install basic server files
cd /var/www/pydap
paster create -t pydap server

# Next, assure that the mod_wsgi module is installed. Note that this is
# different from the mod_proxy_uwsgi module, which is more modern but
# I have had endless problems with.  On CentOS 7,

yum install mod_wsgi

# Edit /var/www/pydap/server/apache/pydap.wsgi  to add these two lines at the very top:

import site
site.addsitedir('/var/www/pydap/env/lib/python2.7/site-packages')

# The whole file will look like this. There may be differences for 
# the paths and python version number.

import site
site.addsitedir('/var/www/pydap/env/lib/python2.7/site-packages')

import os
from paste.deploy import loadapp

config = os.path.join(os.path.dirname(__file__), '../server.ini')
application = loadapp('config:%s' % config)

# Next, edit the /etc/httpd/conf/httpd.conf file to add this:

WSGIScriptAlias /pydap /var/www/pydap/server/apache/pydap.wsgi

<Directory /var/www/pydap/server/apache>
    Order allow,deny
    Allow from all
</Directory>

# This specifies a script to run when someone hits the /pydap URL.
 