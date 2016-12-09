# File: mbari_campaigns.py
#
# Create a symbolic link named campaigns.py to tell the Django server 
# to serve these databases: ln -s mbari_campaigns.py campaigns.py.
# The stoqs/loaders/load.py script uses the load commands associated
# with each database to execute the load and record the provenance.
# Execute 'stoqs/loaders/load.py --help' for more information.

from collections import OrderedDict

# Keys are database (campaign) names, values are paths to load script 
# for each campaign starting at the stoqs/loaders directory.  The full 
# path of 'stoqs/loaders/' is prepended to the value and then executed.

# Name must match loader name in jifx directory
campaigns = OrderedDict([
    ('jifx_dec_2015',   'JIFX/loadARDU.py'),
])
