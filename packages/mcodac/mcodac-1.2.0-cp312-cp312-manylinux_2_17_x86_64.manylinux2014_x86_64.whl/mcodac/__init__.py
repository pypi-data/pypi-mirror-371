# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                                 MCODAC                         #
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Top-level compatibility interface for MCODAC as a standalone python package.
 
@note: MCODAC
Created on 05.08.2024

@version: 1.0
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
                           
@author: garb_ma                                                     [DLR-SY,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""

## @package mcodac
# Top-level compatibility interface for MCODAC as a standalone python package.
## @authors 
# Marc Garbade
## @date
# 05.08.2024
## @par Notes/Changes
# - Added documentation // mg 05.08.2024

import os, sys

# Add local path to global search path
sys.path.insert(0,os.path.dirname(__file__))

from _mcodac import *

if __name__ == '__main__':
    sys.exit()
    pass
