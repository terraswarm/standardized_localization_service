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


import fingerprinting_algorithm as fa
from daemon import runner
import random
import sys
import gdp
import time
import pprint
import json

def generate_offering_static():

  accuracy = 1.9
  latency = 1.2
  power_consumption = 10.0
  provisioning = 'local'

  return accuracy, latency, power_consumption, provisioning


def get_resource():

  logName = 'lemic.localization.resources'
  gcl_name = gdp.GDP_NAME(logName)
  gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RO)
  data = {}
  datum1 = gcl_handle.read(-1)
  data[0] = json.loads(datum1['data'])['data']
  datum2 = gcl_handle.read(-2)
  data[1] = json.loads(datum2['data'])['data']
  datum3 = gcl_handle.read(-3)
  data[2] = json.loads(datum3['data'])['data']
  datum4 = gcl_handle.read(-4)
  data[3] = json.loads(datum4['data'])['data']
  return data


def provisioning_duration_policy():

  return -1

class App():

  def __init__(self, provisioning_service_id, training_path):
    self.stdin_path = '/dev/null'
    self.stdout_path = '/dev/tty'
    self.stderr_path = '/dev/tty'
    self.pidfile_path = '/tmp/provisioning_service_' + str(provisioning_service_id) + '.pid'
    self.pidfile_timeout = 5
    self.training_path = training_path
    self.provisioning_service_id = provisioning_service_id

  def run(self):

    gdp.gdp_init('localhost')
    logs = ['lemic.localization.esi.service_discovery_' + str(self.provisioning_service_id), 'lemic.localization.esi.request_service_' + str(self.provisioning_service_id), 
            'lemic.localization.esi.request_location_' + str(self.provisioning_service_id)]
    
    obj_name_mapping = {}
    for name_str in logs:

      gcl_name = gdp.GDP_NAME(name_str)
      gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RO)
      obj_name_mapping[gcl_handle] = name_str
      gcl_handle.subscribe(0, 0, None)

    while True:

      event = gdp.GDP_GCL.get_next_event(None)
      datum = event["datum"]
      gcl_name = obj_name_mapping[event["gcl_handle"]]
      

      # React on discover service -> offer service
      if gcl_name == logs[0]:

        ils_id = json.loads(datum['data'])['ils_id']
        print 'Got request'
        logName = 'lemic.localization.esi.service_offering_' + str(self.provisioning_service_id)
        gcl_name = gdp.GDP_NAME(logName)
        gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RA)

        accuracy, latency, power_consumption, provisioning = generate_offering_static()
        data = json.dumps({'ils_id': ils_id, 'accuracy': accuracy, 'latency': latency, 'power_consumption': power_consumption, 'elements': provisioning_service_id})
        gcl_handle.append({'data': data})


      # React on request service -> report granted duration
      if gcl_name == logs[1]:

        logName = 'lemic.localization.esi.report_service_' + str(self.provisioning_service_id)
        gcl_name = gdp.GDP_NAME(logName)
        gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RA)

        duration = provisioning_duration_policy()

        data = json.dumps({'duration': duration})
        gcl_handle.append({'data': data})

      
      # React on request location -> read last resource -> generate location -> report location
      if gcl_name == logs[2]:

        ils_id = json.loads(datum['data'])['ils_id']
        timestamp = json.loads(datum['data'])['timestamp']
        print 'Got location request..'
        # Read the last WiFi scan
        wifi_scan = get_resource()

        try:
          location = fa.getPositionEstimateQuantile(wifi_scan, self.training_path)  
        except:
          location = None

        logName = 'lemic.localization.esi.report_location_' + str(self.provisioning_service_id)
        gcl_name = gdp.GDP_NAME(logName)
        gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RA)

        data = json.dumps({'location': location, 'ils_id': ils_id, 'timestamp': timestamp})
        gcl_handle.append({'data': data})



def main(provisioning_service_id, training_files):
	
  app = App(provisioning_service_id, training_files)
  deamon_runner = runner.DaemonRunner(app)
  deamon_runner.do_action()


if __name__ == "__main__":

  provisioning_service_id = 2
  training_files = str('/home/tkn/Desktop/standardized_location_service/benchmark_data/quantile_join/')
  main(provisioning_service_id, training_files)