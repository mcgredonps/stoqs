# Using Apache in a Production Environment

## Introduction

STOQS is set up with a front end web server acting as a "proxy"
for an UWSGI environment running a Django application. A proxy forwards
incoming requests to another service, either running on the same host
or another host. This can be a flexible approach, and it's often possible
for the front end web server to act as a load balancer for multiple
service instances running elsewhere. Many web
servers can do this task. Historically in STOQS this has been done by 
the nginx web server, a fast and scalable web server. This document documents
using Apache instead. 

This has some benefits. STOQS needs a map server, and that map server
must run on Apache; the mapserv appliction is placed in cgi-bin of the
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
request. HTTP is popular, and jk_mod is popular in the web application
server world. Many use conventional internet sockets to transmit the data,
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
"/", it's passed off to the "django" upstream service, which handles the
request. You can choose to have Apache not handle specific directories,
such as http://hostname/media, if you like. The syntax here is specific 
to nginx, but the same thing happens in Apache. 

## STOQS configuration

STOQS is configured in essentially the same way as the nginx production
configuration document.



I recommend you provision the server using the Vagrant provision.sh
script. This installs the assorted packages needed by STOQS.
~~~
./provision.sh
~~~

Afterwards 

Clone STOQS to a directory. The default is /opt/stoqsgit. If you stick
to this you won't have to change as many config files. If you get the
STOQS repository from a different location, for example your own forked
copy of STOQS on github, you'll have to change that location below.
~~~
export STOQS_HOME=/opt/stoqsgit
cd `dirname $STOQS_HOME`
git clone https://github.com/stoqs/stoqs.git stoqsgit
~~~

Set up a virtual enviroment in which the Python/Django application can run.
virtualenv creates a virtual environment in which the Django/stoqs
application will run. "setup.sh production" installs the various
Python modules needed for the application to run.

~~~
cd $STOQS_HOME 
/usr/local/bin/virtualenv venv-stoqs
source venv-stoqs/bin/activate
./setup.sh production
~~~

## Set up Static Content directories

Create the directories in which the Django application's static content will be kept.
On RHEL/CentOS, the default apache content directories are
in /var/www/html. The "stoqs/manage.py collectstatic" command
extracts static web content from the django application and places it
in the directories created. The Apache web server can then serve these
files directly, which is generally faster.

~~~
sudo mkdir /var/www/html/media
sudo mkdir /var/www/html/static
sudo chown $USER /var/www/html/static
export STATIC_ROOT=/var/www/html/static
export DATABASE_URL="postgis://<dbuser>:<pw>@<host>:<port>/stoqs"
stoqs/manage.py collectstatic
~~~

Create the $MEDIA_ROOT/sections and $MEDIA_ROOT/parameterparameter 
directories and set permissions for writing by the web process. In
a RHEL/CentOS environment this is usually the user "apache".

~~~
export MEDIA_ROOT=/var/www/html/media
sudo mkdir $MEDIA_ROOT/sections
sudo mkdir $MEDIA_ROOT/parameterparameter
sudo chown -R $USER /var/www/html/media
sudo chmod 733 $MEDIA_ROOT/sections
sudo chmod 733 $MEDIA_ROOT/parameterparameter
~~~

## Configure stoqs_uwsgi_apache.ini

uwsgi is an environment that runs the Django STOQS application. This is
the service that the front-end web server proxies to, so the Apache configuration
file needs to match up with the parameters in this file.

The configuration file used to uwsgi to start the django/stoqs application
should specify an HTTP port that matches what is used in the Apache
ProxyPass statement below. In this case it's using the HTTP protocol
on port 2000. Apache will forward requests to uswgi at that address,
where it expects uwsgi to be listening. The example uwsgi configuration
file is stoqs_uwsgi_apache.ini in the stoqs application directory. The
relevant changes to it, compared to the nginx configuration file, are
below:

~~~
# stoqs_uwsgi_apache.ini file
[uwsgi]
...
# For apache, use the http port. Older versions of the
# apache/uswgi module don't support unix sockets.
# See http://uwsgi-docs.readthedocs.io/en/latest/Configuration.html
# and
# http://uwsgi-docs.readthedocs.io/en/latest/Apache.html

# I am using the mod_proxy_uwsgi method.
http-socket = 127.0.0.1:4500
~~~

You should have "socket = /opt/stoqsgit/stoqs/stoqs.sock"
and "socket = /opt/stoqsgit/stoqs/stoqs.sock"
from the nginx configuration commented out or removed. This specifies an 
alternative transport mechanism for communicating between the
web server and the uwsgi environment, Unix-domain sockets, that is not 
supported in this apache version.

Start the stoqs uWSGI application. You need to replace <dbuser>, <pw>, <host>, 
<port>, <mapserver_ip_address>, and other values that are specific to your server, 
as set in the provisioning process. 

The SECRET_KEY is secret text used for session security. See 
http://security.stackexchange.com/questions/61909/django-secret-key-security-how-are-methods-more-secure
for details.

The STATIC_ROOT and MEDIA_ROOT refer to directories configured in apache.
On RHEL and derived systems these are usually in /var/www/html. Django
places static content (plain css files and the like) here because the 
content is not dynamically generated, and it can be served faster by
the web server. 

The MAPSERVER_HOST refers to the host running the mapserver. On a single host
machine this will be the FQDN of the host we are installing on.

The --http-socket argument refers to the TCP socket uwsgi will be
listening on. This is the port to which Apache proxies, and it must
match the port number specified in the Apache configuration file.

The uwsgi command starts the Django/stoqs application to which the 
Apache web server will proxy.

~~~
export STOQS_HOME=/opt/stoqsgit
export STATIC_ROOT=/var/www/html/static
export MEDIA_ROOT=/var/www/html/media
export DATABASE_URL="postgis://<dbuser>:<pw>@<host>:<port>/stoqs"
export MAPSERVER_HOST="<mapserver_ip_address>"
export SECRET_KEY="<random_sequence_of_impossible_to_guess_characters>"
export GDAL_DATA=/usr/share/gdal
uwsgi --ini stoqs/stoqs_uwsgi_apache.ini
~~~~

## Apache

This is lifted in part from http://uwsgi-docs.readthedocs.io/en/latest/Apache.html.

Apache has a series of "mod_proxy" plugins that allow the Apache web server to act
as a proxy for services like uwsgi/django running the the background. First of all,
install the uwsgi proxy specific modules in Apache http:

~~~
yum install mod_proxy mod_proxy_uwsgi
~~~

I've added this to the provisioning script in provision.sh in my own git repo.

On Redhat or CentOS releases this downloads and installs the apache modules to
/etc/httpd/modules. On RHEL, you should have an /etc/httpd/conf.modules.d directory,
which holds files that are brought into the main configuration file via an
include. Create a file named 10-wsgi.conf with this as content:

~~~
LoadModule wsgi_module modules/mod_wsgi.so
~~~

When you restart Apache the modules will be loaded. (The yum install creates
a file in the conf.modules.d directory to load the mod_proxy module itself.)

In addition we need to tell Apache to forward requests to the uwsgi/Django
process running on the host.

Add these lines to the httpd.conf file:

~~~
# The order is important here. The lines that end in "!"
# mean "do not send this URL to the upstream proxy; instead
# serve this directory from the web server's document area."
# In this case, apahce serves content from /static and /media,
# but passes the rest to Django.
ProxyPass /static !
ProxyPass /media !
ProxyPass / http://127.0.0.1:4500
~~~

This assumes that the uwsgi application (and the django application)
are listening on localhost port 2000, using the HTTP protocol. See the
configuration file for stoqs_uwsgi.ini.

Restart apache:

~~~
/sbin/service httpd restart
~~~





