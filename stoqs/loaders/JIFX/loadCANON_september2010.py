#!/usr/bin/env python
__author__    = 'Mike McCann'
__copyright__ = '2011'
__license__   = 'GPL v3'
__contact__   = 'mccann at mbari.org'

__doc__ = '''
Master loader for all CANON activities in September 2010

Mike McCann
MBARI 22 April 2012
'''

import os
import sys
# Imports __init.py__ with canon loader from CANON dir. CANON is the
# package we're looking for, so we need the directory that holds CANON.
parentDir = os.path.join(os.path.dirname(__file__), "../")
sys.path.insert(0, parentDir)  # So that CANON is found
from JIFX import ARDULoader

# Assign input data sources
# First arg is database name in psql. should be lower case. 
# See http://stoqs.mbari.org:8000/
# Second is name
# Third is description
# 3d terrains is for camp roberts
cl = ARDULoader('jifx_aug_2016', 'JIFX--August 2016 ',
                    description = 'Swarming UAV at JIFX',
                    x3dTerrains = {
                        'http://dods.mbari.org/terrain/x3d/Monterey25_10x/Monterey25_10x_scene.x3d': {
                            'position': '-2822317.31255 -4438600.53640 3786150.85474',
                            'orientation': '0.89575 -0.31076 -0.31791 1.63772',
                            'centerOfRotation': '-2711557.94 -4331414.32 3801353.46',
                            'VerticalExaggeration': '10',
                            'speed': '.1',
                        }
                    },
                    grdTerrain = os.path.join(parentDir, 'Monterey25.grd')
                )

# Base location for netcdf files for all netcdf files in the campaign.
# Files are the netcdf files to be imported
cl.dorado_base = 'http://localhost:8001/'
cl.dorado_files = [ 'trajectory.nc',
                  ]

# Include variables that will show up in the plots in stoqs. Do 
# not included should be coordinate variables.
cl.dorado_parms = [ 'GPS_GMS,GPS_GWk', 'GPS_TimeUS', 'GPS_Spd','GPS_NSats', 'GPS_HDop', 'IMU_AccX',
                    'IMU_AccY', 'IMU_AccZ', 'IMU_Temp', 'CTUN_ThrOut', 'BARO_Alt', 'BARO_Press',
                    'ARSP_Airspeed', 'ARSP_Temp', 'CURR_Curr', 'CURR_Volt', 'MODE_Mode', 'NTUN_Arspd',
                    'CMD_CNum', 'CMD_CId', 
                  ]

# Execute the load 
cl.process_command_line()

# for very large data sets you can pick up only every N
# records. If test only load every 100. 
if cl.args.test:
    cl.loadARDU(stride=100)

# Stride for production if the data is higher freq than you need
elif cl.args.optimal_stride:
    cl.loadARDU(stride=2)

# Passed in on the command line. Default is 1, set in __init.py__
else:
    cl.loadARDU(stride=cl.args.stride)

# Add any X3D Terrain information specified in the constructor to the database - must be done after a load is executed
# Commented out--DMcG
#cl.addTerrainResources()

print "All Done."

