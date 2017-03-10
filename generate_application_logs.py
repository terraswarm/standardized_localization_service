#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 
Generate a set of GDP logs required for registering a locatio-based information. The parameter 
location_application_id has to be unique. 
"""

__author__ = "Filip Lemic"
__copyright__ = "Copyright 2017, EU eWine Project"

__version__ = "1.0.0"
__maintainer__ = "Filip Lemic"
__email__ = "lemic@tkn.tu-berlin.de"
__status__ = "Development"


import sys
import subprocess


def main(location_application_id):
	
	print 'Creating the Request location log...'
	string = 'lemic.localization.sli.request_location_' + str(location_application_id)
	subprocess.call(['./../gdp/apps/gcl-create', '-k', 'none', '-G', 'localhost', 'test.localization', string])

	print 'Creating the Report location log...'
	string = 'lemic.localization.sli.report_location_' + str(location_application_id)
	subprocess.call(['./../gdp/apps/gcl-create', '-k', 'none', '-G', 'localhost', 'test.localization', string])

	print 'If there was an error, you will make it eventually. Please try to generate the logs manually...'


if __name__ == "__main__":

  location_application_id = sys.argv[1]
  main(location_application_id)  
