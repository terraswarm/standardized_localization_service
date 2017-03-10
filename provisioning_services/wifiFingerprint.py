#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""wifiFingerprint.py: Generate a fingerprint of the WiFi environment (Linux, Mac OS)."""

__author__ = "Filip Lemic"
__copyright__ = "Copyright 2017, EU eWine Project"

__version__ = "1.0.0"
__maintainer__ = "Filip Lemic"
__email__ = "lemic@tkn.tu-berlin.de"
__status__ = "Development"

from subprocess import Popen, PIPE
import sys
import re

class wifiFingerprint():
    """
        This class uses the built-in Apple AirPort to perform a scan for nearby Access Points
        fingerprint has the following structure:
        { "bssid": {"rssi": [ rssi1, rssi2, rssi3, ... ], "ssid": "<ssid>", "channel": "<channel>" },
          "bssid2": ...}
    """

    def __init__(self):
        self.airportPath = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport'
        self.iwlistPath = 'iwlist'
        self.INTERFACE = 'wlan0'
        self.fingerprint = {}

    def _checkAirportEnabled(self):
        arguments = [self.airportPath, "--getinfo"]
        execute = Popen(arguments, stdout=PIPE)
        out, err = execute.communicate()
        if (out.strip() == "AirPort: Off"):
            print "AirPort is disabled!"
            return False
        else:
            return True

    def _getAirportScan(self):
        arguments = [self.airportPath, "-s"]  # scan (-s)
        execute = Popen(arguments, stdout=PIPE)
        out, err = execute.communicate()
        list = []
        c = re.compile(r'\s+(?P<ssid>.*)\s+(?P<bssid>(?:[0-9a-f]{1,2}[:]){5}[0-9a-f]{1,2})\s(?P<rssi>[-]?\d+)\s+(?P<channel>[\d,-]+)\s+.*')
        for line in out.split('\n'):
            m = c.match(line)
            if m:
                list.append(m.groupdict())
        return list

    def _buildFingerprintFromScan(self, scan, fingerprint={}):
        for ap in scan:
            if ap['bssid'] not in fingerprint:
                # add bssid
                fingerprint[ap['bssid']] = {}
                fingerprint[ap['bssid']]['ssid'] = ap['ssid']
                fingerprint[ap['bssid']]['channel'] = ap['channel']
                fingerprint[ap['bssid']]['rssi'] = [int(ap['rssi'])]
            else:
                # add rssi to list
                fingerprint[ap['bssid']]['rssi'].append(int(ap['rssi']))
        return fingerprint

    def _checkWifiEnabled(self):
        arguments = [self.iwlistPath, self.INTERFACE, "scanning"]
        execute = Popen(arguments, stdout=PIPE, stderr=PIPE)
        out, err = execute.communicate()
        if err.strip() == ("%s     Interface doesn't support scanning." % self.INTERFACE):
            print "Interface %s is down!" % self.INTERFACE
            return False
        return True            

    def _getWifiScan(self):
        arguments = [self.iwlistPath, self.INTERFACE, "scanning"]
        execute = Popen(arguments, stdout=PIPE)
        out, err = execute.communicate()
        list = []
        pattern = r'Address:\s(?P<bssid>(?:[0-9A-F]{2}:){5}[0-9A-F]{2})\s+Channel:(?P<channel>\d+)(?:\s+.*){2}Signal\slevel=(?P<rssi>[-]?\d+)\sdBm(?:\s+.*){2}ESSID:\"(?P<ssid>.+)\"'
        c = re.compile(pattern, re.MULTILINE)
        m = c.finditer(out)
        for match in m:
            list.append(match.groupdict())
        return list

    def _buildFingerprintFromWifiScan(self, wifiScan, fingerprint={}):
        pass

    def scan(self, numOfScans):
        if sys.platform == 'darwin':
            if (self._checkAirportEnabled()):
                for i in range(numOfScans):
                    self._buildFingerprintFromScan(self._getAirportScan(), self.fingerprint)
                return self.fingerprint
            else:
                return {}
        elif sys.platform == 'linux2':
            if (self._checkWifiEnabled()):
                for i in range(numOfScans):
                    self._buildFingerprintFromScan(self._getWifiScan(), self.fingerprint)
            	return self.fingerprint
            else:
                return {}

    def reset(self):
        self.fingerprint = {}

    def getFingerprint(self):
        if (len(self.fingerprint) > 0):
            return self.fingerprint
        else:
            return self.scan(1)