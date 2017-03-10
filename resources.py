#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GDP daemon process that continuously collects RSS scans from a WiFi interface and stores them in a GDP log. 
"""

__author__ = "Filip Lemic"
__copyright__ = "Copyright 2017, EU eWine Project"

__version__ = "1.0.0"
__maintainer__ = "Filip Lemic"
__email__ = "lemic@tkn.tu-berlin.de"
__status__ = "Development"

from wifiFingerprint import wifiFingerprint
from datetime import datetime
import time
import json
import sys
from daemon import runner
import gdp


def get_rss_scan():
  """
    Collects RSS scans.

    returns: 
      a scan of RSS environment for a given space and time instance.
  """
    
    fpf = wifiFingerprint()
    fpf.scan(1)
    fp = fpf.getFingerprint()
    
    rss_scan = {}
    rss_scan['timestamp_utc'] = timestamp_utc = int(time.mktime(datetime.utcnow().timetuple()))
    rss_scan['data'] = {}
    
    for key in fp.keys():
    
        rss_scan['data'][key] = {}
        rss_scan['data'][key]['sender_bssid'] = key
        rss_scan['data'][key]['sender_id'] = fp[key]['ssid']
        rss_scan['data'][key]['rssi'] = int(fp[key]['rssi'][0])
        rss_scan['data'][key]['channel'] = fp[key]['channel']

    return json.dumps(rss_scan)


def push_rss_to_log():
  """
    Storing the collected RSS scans into a GDP log.
  """

  logName = 'lemic.localization.resources'
  scan = get_rss_scan()

  gcl_name = gdp.GDP_NAME(logName)
  gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RA)

  gcl_handle.append({'data': scan})

  return 'New scan pushed to the resource log...'


class App():

  def __init__(self):
    self.stdin_path = '/dev/null'
    self.stdout_path = '/dev/tty'
    self.stderr_path = '/dev/tty'
    self.pidfile_path = '/tmp/resources.pid'
    self.pidfile_timeout = 5

  def run(self):

    gdp.gdp_init('localhost')
    while True:
      print push_rss_to_log()
      time.sleep(0.01)



def main():

  app = App()
  deamon_runner = runner.DaemonRunner(app)
  deamon_runner.do_action()


if __name__ == "__main__":
  main()

