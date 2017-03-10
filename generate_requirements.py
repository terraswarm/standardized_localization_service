#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

__author__ = "Filip Lemic"
__copyright__ = "Copyright 2017, EU eWine Project"

__version__ = "1.0.0"
__maintainer__ = "Filip Lemic"
__email__ = "lemic@tkn.tu-berlin.de"
__status__ = "Development"


from location_application import request_location
import time

# Start each location application as a daemon - play with their number and parameters
# Start the integrated location service as a daemon - fetch the requests, issues responses, parallelize?
# Each provisioning service is a daemon - specify multiple sources, they can run here as well.
# Same with the resources, i.e. RSS scans - that is also a shared daemon process writing in a log 


while True:
	time.sleep(2)
	logName = 'lemic.localization.sli.request_location_1'
	parameters = {}
	parameters['location_type'] = '1st'
	parameters['dimensionality'] = '2D'
	parameters['accuracy'] = 0.9
	parameters['period'] = 3.4
	parameters['on_event'] = 'periodically'
	parameters['step'] = 0.0
	parameters['duration'] = 0
	parameters['movement'] = 'no'
	parameters['timestamp_start'] = time.time()
	print logName + str(': ') + request_location(parameters, logName)
	time.sleep(2)

	logName = 'lemic.localization.sli.request_location_2'
	parameters = {}
	parameters['location_type'] = '2nd'
	parameters['dimensionality'] = '2D'
	parameters['accuracy'] = 1.5
	parameters['period'] = 4.2
	parameters['on_event'] = 'on_event'
	parameters['step'] = 2.0
	parameters['duration'] = 0
	parameters['movement'] = 'no'
	parameters['timestamp_start'] = time.time()
	print logName + str(': ') +  request_location(parameters, logName)
