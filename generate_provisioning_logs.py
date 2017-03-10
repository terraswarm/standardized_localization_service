#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generate a set of GDP logs required for binding a location information provisioning service with the 
integrated location service. The parameter provisioning_service_id has to be unique. 
"""

__author__ = "Filip Lemic"
__copyright__ = "Copyright 2017, EU eWine Project"

__version__ = "1.0.0"
__maintainer__ = "Filip Lemic"
__email__ = "lemic@tkn.tu-berlin.de"
__status__ = "Development"


import sys
import subprocess


def main(provisioning_service_id):
	
	print 'Creating the Discovery log...'	
	string = 'lemic.localization.esi.service_discovery_' + str(provisioning_service_id)
	print subprocess.call(['./../gdp/apps/gcl-create', '-k', 'none', '-G', 'localhost', 'test.localization', string])

	print 'Creating the Offering log...'
	string = 'lemic.localization.esi.service_offering_' + str(provisioning_service_id)
	print subprocess.call(['./../gdp/apps/gcl-create', '-k', 'none', '-G', 'localhost', 'test.localization', string])

	print 'Creating the Request service log...'
	string = 'lemic.localization.esi.request_service_' + str(provisioning_service_id)
	print subprocess.call(['./../gdp/apps/gcl-create', '-k', 'none', '-G', 'localhost', 'test.localization', string])

	print 'Creating the Report service log...'
	string = 'lemic.localization.esi.report_service_' + str(provisioning_service_id)
	print subprocess.call(['./../gdp/apps/gcl-create', '-k', 'none', '-G', 'localhost', 'test.localization', string])

	print 'Creating the Request location log...'
	string = 'lemic.localization.esi.request_location_' + str(provisioning_service_id)
	print subprocess.call(['./../gdp/apps/gcl-create', '-k', 'none', '-G', 'localhost', 'test.localization', string])

	print 'Creating the Report location log...'
	string = 'lemic.localization.esi.report_location_' + str(provisioning_service_id)
	print subprocess.call(['./../gdp/apps/gcl-create', '-k', 'none', '-G', 'localhost', 'test.localization', string])

	print 'If there was an error, you will make it eventually :) Please try to generate the logs manually...'


if __name__ == "__main__":

  provisioning_service_id = sys.argv[1]
  main(provisioning_service_id)  
