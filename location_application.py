#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""rawRssiScanner.py: Scans the WiFi environment for RSSI values from WiFi beacon packets."""

__author__ = "Filip Lemic"
__copyright__ = "Copyright 2017, EU eWine Project"

__version__ = "1.0.0"
__maintainer__ = "Filip Lemic"
__email__ = "lemic@tkn.tu-berlin.de"
__status__ = "Development"

from threading import Thread
from daemon import runner
import sys, os
import gdp
import time
import json


def request_location(parameters, logName):
  """
  Implementation of the request location primitive of the SLI. 

  parameters:
    location_type - type of location information: global/local/semantic
    dimensionality - for global/local location information type, is it 2D/3D?
    accuracy - desired accuracy of the requested location information
    period - desired period of location information provisioning
    on_event - when is location information provided - periodically with the period, on change of step from preceding location
    step - size of change of location information
    duration - duration of location information provisioning 
    movement - do you want historical information, .e.g speed, orientation
  logName - name of the log for requesting location information
  """

  location_type = parameters['location_type']
  dimensionality = parameters['dimensionality'] 
  accuracy = parameters['accuracy']
  period = parameters['period'] 
  provisioning_type = parameters['provisioning_type'] 
  step = parameters['step']
  duration = parameters['duration'] 
  movement = parameters['movement']
  # Evaluation purpose only, can be removed later
  timestamp_start = parameters['timestamp_start']

  gcl_name = gdp.GDP_NAME(logName)
  gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RA)

  # First parameter for evaluation purposes only, can be removed later.
  data = json.dumps({'timestamp_start': timestamp_start, 'location_type': location_type, 'dimensionality': dimensionality, 'accuracy': accuracy, 'period': period, 'provisioning_type': provisioning_type, 'step':  step, 'duration': duration, 'movement': movement})
  gcl_handle.append({'data': data})

  return 'New request written in the Request location log...'



def store_reported_location(fileName, logNames):
  """Example implementation of the listener for reported locations. The function listens for reported locations 
     and stores them in a file.

     logNames - List of log names where the locations are reported (implements the report location primitive(s) of the SLI). 
     fileName - Name of the file where the received locations are stored.
  """

  obj_name_mapping = {}

  for name_str in logNames:

    gcl_name = gdp.GDP_NAME(name_str)
    gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RO)
    obj_name_mapping[gcl_handle] = name_str
    gcl_handle.subscribe(0, 0, None)

  while True:
    event = gdp.GDP_GCL.get_next_event(None)
    timestamp_end = time.time()
    datum = event["datum"]
    gcl_name = obj_name_mapping[event["gcl_handle"]]
    data = datum["data"]
    timestamp_start = float(json.loads(data)['timestamp_start'])
    print gcl_name + str(': ') + 'New location information received.'
    print 'Latency: ' + str(timestamp_end - timestamp_start)
    string = gcl_name + ',' + str(timestamp_end) + ',' + data + '\n'
    with open(fileName, 'a') as the_file:
      the_file.write(string)



class App():

  def __init__(self):
    self.stdin_path = '/dev/null'
    self.stdout_path = '/dev/tty'
    self.stderr_path = '/dev/tty'
    self.pidfile_path = '/tmp/example_app.pid'
    self.pidfile_timeout = 5


  def run(self):

    gdp.gdp_init('localhost')
    t1 = Thread(target = store_reported_location, args = ('/home/tkn/Desktop/standardized_location_service/performance_benchmark.txt', 
      ['lemic.localization.sli.report_location_1', 'lemic.localization.sli.report_location_2'],)) 
    
    t1.start()


    time.sleep(0.1)
    logName = 'lemic.localization.sli.request_location_1'
    parameters = {}
    parameters['location_type'] = 'local'
    parameters['dimensionality'] = '2D'
    parameters['accuracy'] = 1.0
    parameters['period'] = 2.0
    parameters['provisioning_type'] = 'periodic'
    parameters['step'] = 0.0
    parameters['duration'] = 150.0
    parameters['movement'] = 'no'
    # Evaluation purpose only, can be removed later
    parameters['timestamp_start'] = time.time()
    print logName + str(': ') + request_location(parameters, logName)
    time.sleep(0.1)


    logName = 'lemic.localization.sli.request_location_2'
    parameters = {}
    parameters['location_type'] = 'semantic'
    parameters['dimensionality'] = '2D'
    parameters['accuracy'] = 0.8
    parameters['period'] = 1.5
    parameters['provisioning_type'] = 'periodic'
    parameters['step'] = 0.0
    parameters['duration'] = 150.0
    parameters['movement'] = 'no'
    # Evaluation purpose only, can be removed later
    parameters['timestamp_start'] = time.time()
    print logName + str(': ') +  request_location(parameters, logName)
    time.sleep(0.01)

    while True:
      pass



def main():

  app = App()
  deamon_runner = runner.DaemonRunner(app)
  deamon_runner.do_action()


if __name__ == "__main__":
  main()
