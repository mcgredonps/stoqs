Create a jifx_campaigns.py file with the loaders. Check this in to source code control.
Create a symbolic link in stoqs, campaigns.py, that links back to this. This should 
not be checked into source code control.

loaders/load.py --db jifx_aug_2016 --clobber


format checker:

pip install compliance-checker
yum install udunits2

Python debugger
import pdb; pdb.set_trace();

JIFX campaign link:

campaigns.py -> jifx_campaigns.py
