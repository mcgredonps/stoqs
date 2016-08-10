# Using Apache in a Production Environment

## Introduction

STOQS is set up with a front end web server acting as a proxy
for an UWSGI environment running a Django application. Many web
servers can do this task. Historically in STOQS this has been done by 
nginx, a fast and scalable web server. This document documents
using Apache instead. 

This has some benefits. STOQS needs a map server, and that map server
must be Apache; the mapserv appliction is placed in cgi-bin of the
apache server. If you're running STOQS on a single server, this means
you wind up running both Apache and nginx. Since only one can
listen on port 80/443, this often means Apache must run on a non-standard
port that is accessible from the client, outside the hosting organization's
enterprise firewall. Getting a non-standard port, such as 8000, open
through the firewall can range in difficulty from "hard" all the way to
"impossible without someone holding a pistol to the head of the 
enterprise CEO."

## Background and Theory

Web servers often act as proxies for services running somewhere 
safer than the open internet. The web server accepts the request,
then turns around and hands it off to service. The service responds,
and the response is relayed back to the client by the web server. 
There are a variety of protocols and media that can be used to proxy the
request. HTTP is popular, and jk_mod is popualr in the web application
world. Many use conventional internet sockets to transmit the data,
and some use Unix domain sockets or other media.

In the case of nginx, configuring how this is done is 
in the config file with this piece of configuration:

~~~
# the upstream component nginx needs to connect to
upstream django {
    server unix:///opt/stoqsgit/stoqs/stoqs.sock;       # a file socket has less overhead
    #server 127.0.0.1:8001;                             # a web port socket
}
 ....
 # Finally, send all non-media requests to the Django server.
    location / {
        uwsgi_pass  django;
        include     /opt/stoqsgit/stoqs/uwsgi_params; # the uwsgi_params file you installed
    }
~~~~

This specifies a service running on localhost (127.0.0.1) listening on 
a Unix domain socket. When a request to the root comes in at
"/", it's passed off to the "django" upstream, which handles the
request. You can choose to have Apache not handle specific directories,
such as http://hostname/media, if you like. The syntax here is specific 
to nginx, but the same thing happens in Apache. 

## STOQS configuration

STOQS is configured in essentially the same way as the nginx document.

Clone STOQS to a directory. The default is /opt/stoqsgit. If you stick
to this you won't have to change as many config files.

~~~
export STOQS_HOME=/opt/stoqsgit
cd `dirname $STOQS_HOME`
git clone https://github.com/stoqs/stoqs.git stoqsgit
~~

Provision the server. This is usually done with provision.sh, 
which is intended for the Vagrant environment, but works well 
enough on conventional hosts.

Set up a virtual enviroment for the Python application to run in.

~~~
cd $STOQS_HOME 
/usr/local/bin/virtualenv venv-stoqs
source venv-stoqs/bin/activate
./setup.sh production
~~~

## Apache

This is lifted in part from http://uwsgi-docs.readthedocs.io/en/latest/Apache.html.

Apache has a series of "mod_proxy" plugins that allow the Apache web server to act
as a proxy for services like uwsgi/django running the the background. First of all,
install the uwsgi proxy specific modules in Apache http:

~~~
yum install mod_proxy mod_proxy_uwsgi 
~~~~

On Redhat or CentOS releases this downloads and installs the apache modules to 
/etc/httpd/modules. On RHEL, you should have an /etc/httpd/conf.modules.d directory,
which holds files that are brought into the main configuration file via an 
include. Create a file named 10-wsgi.conf with this as content:

~~~
LoadModule wsgi_module modules/mod_wsgi.so
~~~~

When you restart Apache the modules will be loaded.

In addition we need to tell Apache to forward requests to the uwsgi/Django
process running on the host. 

Add these lines to the httpd.conf file:

~~~~
ProxyPass / http://127.0.0.1:2000
ProxyPassReverse / http://127.0.0.1:2000
~~~~

This assumes that the uwsgi application (and the django application) 
are listening on localhost port 2000, using the HTTP protocol. See the
configuration file for stoqs_uwsgi.ini.

Create the directories in which static content will be kept.
On RHEL/CentOS, the default apache content directories are
in /var/www/html.

~~~
sudo mkdir /var/www/html/media
sudo mkdir /var/www/html/static
sudo chown $USER /var/www/html/static
export STATIC_ROOT=/var/www/html/static
export DATABASE_URL="postgis://<dbuser>:<pw>@<host>:<port>/stoqs"
stoqs/manage.py collectstatic
~~~

Create the $MEDIA_ROOT/sections and $MEDIA_ROOT/parameterparameter directories and set permissions for writing by the web process.

~~~~
export MEDIA_ROOT=/var/www/html/media
sudo mkdir $MEDIA_ROOT/sections
sudo mkdir $MEDIA_ROOT/parameterparameter
sudo chown -R $USER /var/www/html/media
sudo chmod 733 $MEDIA_ROOT/sections
sudo chmod 733 $MEDIA_ROOT/parameterparameter
~~~~

## Configure stoqs_uwsgi_apache.ini

The configuration file used to uwsgi to start the django/stoqs application
should specify an HTTP port that matches what is used in the Apache
ProxyPass statement above.

~~
# stoqs_uwsgi.ini file
[uwsgi]
...
# For apache, use the http port. Older versions of the
# apache/uswgi module don't support unix sockets.
# See http://uwsgi-docs.readthedocs.io/en/latest/Configuration.html
# and
# http://uwsgi-docs.readthedocs.io/en/latest/Apache.html

# I am attempting to use the mod_proxy_uwsgi method.
http-socket = 127.0.0.1:2000
~~~

You should have "socket = /opt/stoqsgit/stoqs/stoqs.sock"
commented out. This specifies an alternative transport
mechanism for communicating with the Django application,
Unix-domain sockets, that is not supported
in this apache version.


Start the stoqs uWSGI application, replacing <dbuser>, <pw>, <host>, <port>, <mapserver_ip_address>, and other values that are specific to your server, e.g.:

~~~~
export STOQS_HOME=/opt/stoqsgit
export STATIC_ROOT=/var/www/html/static
export MEDIA_ROOT=/var/www/html/media
export DATABASE_URL="postgis://<dbuser>:<pw>@<host>:<port>/stoqs"
export MAPSERVER_HOST="<mapserver_ip_address>"
export SECRET_KEY="<random_sequence_of_impossible_to_guess_characters>"
export GDAL_DATA=/usr/share/gdal
uwsgi --http-socket :2000 --ini stoqs/stoqs_uwsgi_apache.ini
~~~~~

Note the port number used for the --http-socket flag. This must 
match the socket specified above in the HTML configuration file
for For ProxyPass and ProxyPassReverse.

