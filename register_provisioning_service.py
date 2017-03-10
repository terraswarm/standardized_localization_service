#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Register a provisioning service with the integrated location service. Before registering a provisioning service 
please generate the provisioning logs for that provisioning service.
"""

__author__ = "Filip Lemic"
__copyright__ = "Copyright 2017, EU eWine Project"

__version__ = "1.0.0"
__maintainer__ = "Filip Lemic"
__email__ = "lemic@tkn.tu-berlin.de"
__status__ = "Development"


import sys
import subprocess
import gdp
import json

def main(provisioning_service_id):
	
	print 'Creating the Register service log...'	
	string = 'lemic.localization.esi.register_service'
	print subprocess.call(['./../gdp/apps/gcl-create', '-k', 'none', '-G', 'localhost', 'test.localization', string])
	print 'The Register service log most probably already exists, but no worries, ignore the previous error!'

	# Check if a service with that ID already exists!
	gdp.gdp_init('localhost')
  	gcl_name = gdp.GDP_NAME(string)
	gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RO)

	# Read the whole register service log
	recno = 1
	services = []
	while True:
	    try:
	        datum = gcl_handle.read(recno)
	        services.append(json.loads(datum['data'])['service_id'])
	        recno += 1
	    except:
	        break

	if provisioning_service_id not in services:   	
		# Write an entry in the log
		logName = 'lemic.localization.esi.register_service'
		gcl_name = gdp.GDP_NAME(logName)
		gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RA)

		data = json.dumps({'service_id': provisioning_service_id})
		gcl_handle.append({'data': data})
		print 'Provisioning service ' + str(provisioning_service_id) + ' successfully registered for provisioning.' 
	else:
		print 'Log ID has to be unique! Be creative!'

if __name__ == "__main__":

  provisioning_service_id = sys.argv[1]
  main(provisioning_service_id)  