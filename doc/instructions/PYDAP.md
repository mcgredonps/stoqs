## PyDap

PyDap is a system for serving up netcdf files remotely in 
accordance with the OPenDAP Data Access Protocol. See [https://www.opendap.org]
for more information on OPenDAP. The PyDap site is at
[http://www.pydap.org].

Instructions for installing PyDap with Apache are here:

[http://www.pydap.org/server.html#running-pydap-with-apache]

Assuming a standard apache install, with the standard HTML content
in /var/www/html and the configuration file in /etc/httpd/conf, installing
it goes something like this:

```bash
# Create a pydap directory outside the standard content directory.
# The virualenv.py file creates an isolated virtual environment directory with the 
# in which the neccesary python supporting packages can be placed. Pip will 
# place the supporting packages there, in the env directory

mkdir /var/www/pydap
python /usr/local/lib/python2.7/site-packages/virtualenv.py /var/www/pydap/env

# Alternatively create the virtual environment with system site packages
#python virtualenv.py --system-site-packages /var/www/pydap/env

# Source the file necessary to set the environment variables, and
# then use pip to install various packages into the sandbox/isolated
# python environment in the env directory, including Pydap, the python-based
# OpenDap server for NetCDF files.
source /var/www/pydap/env/bin/activate
pip install Pydap

# Install basic server files. Paster is a utility for creating wsgi
# applications. In this case we are creating a wsgi application
# that will be placed in a directory named "server"
cd /var/www/pydap
paster create -t pydap server

# The server.ini file created in the server directory looks like this:
#server:main]
#use = egg:Paste#http
## Change to 0.0.0.0 to make public
#host = 127.0.0.1
#port = 8001
#
#[app:main]
#use = egg:pydap#server
#root = %(here)s/data
#templates = %(here)s/templates
#x-wsgiorg.throw_errors = 0


# Next, assure that the mod_wsgi module is installed. Note that this is
# different from the mod_proxy_uwsgi module, which is more modern but
# with which I have had endless problems.  mod_wsgi is an apache
# module that provides a wsgi interface for hosting wsgi-compliant
# python applications. On CentOS 7 it can be installed from yum

yum install mod_wsgi

# Edit /var/www/pydap/server/apache/pydap.wsgi  to add these two lines at the very top:

import site
site.addsitedir('/var/www/pydap/env/lib/python2.7/site-packages')

# The whole file will look like this. There may be differences for 
# the paths and python version number. This specifies the directory
# in which pip placed the supporting python files.

import site
site.addsitedir('/var/www/pydap/env/lib/python2.7/site-packages')

import os
from paste.deploy import loadapp

config = os.path.join(os.path.dirname(__file__), '../server.ini')
application = loadapp('config:%s' % config)

# Next, edit the /etc/httpd/conf/httpd.conf file to add this. The
# path to the pydap.wsgi file is the entry point for the script, 
# which is what was edited directly above. The <Directory> directives
# are necessary to give the apache server access to the files
# in those directories. The /var/www/pydap/server/data directory
# holds content served up, including the netcdf files. It includes
# a ".static" directory with static content, including javascript
# files and css files. Be careful, this will be hidden with a normal
# ls command, use ls -a instead. The Alias directive in the conf
# file below is used because the HTML generated will make references
# to 'http://foo.org/pydap/.static/js/something.js', for example.
# The Alias directive forces apache to look in the directory specified
# rather than in /var/www/html/.static.
#

WSGIScriptAlias /pydap /var/www/pydap/server/apache/pydap.wsgi
Alias /.static /var/www/pydap/server/data/.static

<Directory /var/www/pydap/server/apache>
    Order allow,deny
    Allow from all
</Directory>

<Directory /var/www/pydap/server/data>
   Order allow,deny
   Allow from all
</Directory>

# Restart httpd, go to /pydap. Place any netcdf files in the
# /var/www/pydap/server/data directory.
```