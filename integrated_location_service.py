#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""integrated_location_service.py: Core of the architecture, implementation of the integrated location service. 
  Subscription to the location requests, discovery of provisioning services, selection of provisioning services based 
  on the requirements from the applications and provisioning features of the available provisioning services, subscription to 
  the reporting location logs, fusion of location information, provisioning of the location information to the applications. 
  Cashing, mapping, map provisioning, context calculation capabilities.
"""

__author__ = "Filip Lemic"
__copyright__ = "Copyright 2017, EU eWine Project"

__version__ = "1.0.0"
__maintainer__ = "Filip Lemic"
__email__ = "lemic@tkn.tu-berlin.de"
__status__ = "Development"


from threading import Thread
from Queue import Queue
from daemon import runner
import selection_algorithms as SA
import gdp, signal
import room_mapping
import os, sys, time, json
import numpy as np
import pprint




def most_common(lst):
    """   
      Finding the most common element in a list.
  
      arguments:
        lst - list containing all elements

      returns:
        most common element in the list
    """
    
    return max(set(lst), key=lst.count)





def generate_virtual_requests(memorized_requests):
  """
    In case of requests for a specific duration and with a specific period, update your list of requests.
  
    arguments:
      memorized_requests - contains the specification of requests that have to be addressed in the future

    returns
      memorized requests to be addressed in this time-slot
  """

  current_requests = {}

  for i in memorized_requests:
    if i['provisioning_type'] == 'on_event':
      step = 1
    else:
      step = i['period']
    
    list_times = np.arange(i['timestamp_start'], i['timestamp_start'] + i['duration'], step)

    for serving_time in list_times:
      if serving_time > time.time() and serving_time < time.time() + 0.8:
        current_requests[i['key']] =  {}   
        current_requests[i['key']]['location_type'] = i['location_type']
        current_requests[i['key']]['dimensionality'] = i['dimensionality']
        current_requests[i['key']]['accuracy'] = i['accuracy']
        current_requests[i['key']]['period'] = i['period']
        current_requests[i['key']]['provisioning_type'] = 'once'
        current_requests[i['key']]['step'] = i['step']
        current_requests[i['key']]['duration'] = 0.0
        current_requests[i['key']]['request_time'] = time.time()
        # Evaluation purpose only, can be removed later
        current_requests[i['key']]['timestamp_start'] = time.time()
        break

  return current_requests





def update_memorized_requests(memorized_requests, requests):
  """
    In case of requests for a specific duration and with a specific period, update your list of requests.
    
    arguments:
      requests - contains the specification of newly arrived future requests
      memorized_requests - contains the specification of requests that have to be addressed in the future

    returns:
      updated list of memorized requests

  """

  new_requests = []

  # Cleaning memorized requests
  for i in memorized_requests:
    if time.time() - i['timestamp_start'] < i['duration']:
      new_requests.append(i)

  # Adding newly arrived requests
  tmp_req = {}
  for i in requests:
    tmp_req['key'] = i
    tmp_req['timestamp_start'] = requests[i]['request_time']
    tmp_req['period'] = requests[i]['period']
    tmp_req['accuracy'] = requests[i]['accuracy']
    tmp_req['duration'] = requests[i]['duration']
    tmp_req['dimensionality'] = requests[i]['dimensionality']
    tmp_req['location_type'] = requests[i]['location_type']
    tmp_req['provisioning_type'] = requests[i]['provisioning_type']
    tmp_req['step'] = requests[i]['step']

    new_requests.append(tmp_req)

  return new_requests




def solve_with_cashing(request, cashed_locations):
  """
    Addressing a request using cashed location information.

    arguments:
      request - request for location information
      cashed_locations - current cashed locations 

    returns:
      location information if cashed locations are enough for addressing a request
  """

  # Variable defining the duration of cashed information
  old_cash = 2
  time_now = time.time()
  for i in cashed_locations:
    # is the cashed location information is not stale and if its accuracy feature is
    # higher that the accuracy requirement of the current request
    if time_now - i[0]['timestamp'] < old_cash and request['accuracy'] > i[0]['accuracy']:
      # First entry is for evaluation purposes only, can be removed later
      location = {'timestamp_start': request['timestamp_start'], 'est_coordinate_x': i[0]['est_x'], 'est_coordinate_y': i[0]['est_y'], 'est_room_label': i[0]['est_room']}
      return location
  
  return None




def update_cashing(cashed_locations, locations):
  """
    Updating cashed location information -  deleting the staled ones, adding the new ones.
    
    arguments:
      cashed_locations - current cashed locations 
      locations - location information to be added to the cashed locations 
    returns:
      updated list of cashed location information
  """

  # How old can a cashed location be?
  old_cash = 2
  time_now = time.time()
  # Cleaning the stale location information from the cash
  for i in cashed_locations:
    if time_now - i[0]['timestamp'] > old_cash:
      cashed_locations.remove(i) 


  if locations[0]['est_x'] is not None and locations[0]['est_y'] is not None:
    locations[0]['location_type'] = 'local'
  elif locations[0]['est_room'] is not None:
    locations[0]['location_type'] = 'semantic'
  else:
    return cashed_locations
  
  # Adding new location information to the cash
  cashed_locations.append(locations)
  return cashed_locations




def solve_with_mapping(request, cashed_locations):
  """
    Solve a request in case a cashed location information of different type and sufficiently good features is available.
  
    arguments:
      request - request to be addressed
      cashed_locations - current cashed locations

    returns:
      location information in case it exists 
  """
  
  location = None

  # Mapping from semantic to local location type
  if request['location_type'] == 'local':
    for loc in cashed_locations:
      # If the cashed semantic location information is semantic and if the accuracy of the cashed location information is higher than 90%    
      # and if the accuracy of the requested location location information is higher than 5 meters and if the cashed location information is not stale.  
      if loc[0]['location_type'] == 'semantic' and loc[0]['accuracy'] > 0.9 and request['accuracy'] > 5 and request['timestamp'] - loc[0]['timestamp'] < 2:
        (x,y) = room_mapping.get_coordinate(loc[0]['est_room'])
        location = {'timestamp_start': request['timestamp_start'], 'est_coordinate_x': x, 'est_coordinate_y': y, 'est_room_label': loc[0]['est_room']}
        break 

  # Mapping from local to semantic location type
  elif request['location_type'] == 'semantic':
    for loc in cashed_locations:
      if loc[0]['location_type'] > 'local' and loc[0]['accuracy'] > 1 and request['timestamp'] - loc[0]['timestamp'] < 2:
        room_label = room_mapping.get_room(loc[0]['est_x'], loc[0]['est_y'])
        location = {'timestamp_start': request['timestamp_start'], 'est_coordinate_x': loc[0]['est_x'], 'est_coordinate_y': loc[0]['est_y'], 'est_room_label': room_label}
        break

  return location






def read_logs(obj_name_mapping, ils_id, cashed_locations, request_q, offering_q, location_q, mem_requests_q):
  """
    Subscription to all required GDP logs (receiving requests for location information, requesting provisioning features from
    location information provisioning services, and receiving location information from provisioning services).  
  
    obj_name_mapping - object containing subscriptions to all relevant logs
    ils_id - ID of this integrated location service, needed for shared provisioning services
    cashed_locations - current cashed locations 
    request_q - queue containing all unsolved requests, used for multi-thread signaling 
    offering_q - queue containing current offerings (provisioning features), used for multi-thread signaling 
    location_q - queue containing current location information provided by the provisioning services
    mem_requests_q - queue containing memorized requests, i.e. pushing the 'intelligence' to the integrated location service 
  """

  # Variable containing provisioning features of all available provisioning services
  offerings = {}
  # Variable containing requirements from all applications.
  requests = {}
  # Variable contacting all location information provided by the invoked provisioning services.
  locations = []
  # Variable containing 'intelligent' requests for one time-slot
  mem_requests = {}

  mem_requests_old = {}
  try:  
    mem_requests_old = mem_requests_q.get_nowait()
  except:
    pass

  # Generate virtual requests for this time-bucket
  if len(mem_requests_old) > 0:
    requests = generate_virtual_requests(mem_requests_old)

  # Loop with a timeout of 0.5 seconds, constant listening for new entries in the subscribed logs
  while True:

    # Timeout specification
    timeout = {'tv_sec': 0, 'tv_nsec': 800000000, 'tv_accuracy':0.0}
    # Capturing events - new entries in the subscribed logs
    event = gdp.GDP_GCL.get_next_event(timeout)
  
    # Try/except because of the NULL event, i.e. the timeout event
    try:
    
      # Data of a particular new entry
      datum = event["datum"]
      # Log name
      gcl_name = obj_name_mapping[event["gcl_handle"]]
      # Entity generated data on a entry 
      tmp_request = json.loads(datum['data'])

      # Handling the offerings from provisioning services
      if 'offering' in gcl_name:
        offerings[gcl_name] = tmp_request

      # Handling the requests from location-based applications
      elif 'request' in gcl_name:

        # Memorize periodic or on_event requests
        if tmp_request['provisioning_type'] == 'periodic' or tmp_request['provisioning_type'] == 'on_event':
          mem_requests[gcl_name] = tmp_request

        # Request time parameter of each request - used by provisioning services selection algorithms
        tmp_request['request_time'] = time.time()
        # Try to handle each request by cashing
        if len(cashed_locations) > 0:
          tmp_location = solve_with_cashing(tmp_request, cashed_locations)
          if tmp_location is None:            
            tmp_location = solve_with_mapping(tmp_request, cashed_locations)
        else:
          tmp_location = None

      
        # Case when cashed location information cannot address a request (either stale or does not 'good enough')
        if tmp_location is None:
          requests[gcl_name] = tmp_request
        else:
          # Report cashed location to the application
          logName = 'lemic.localization.sli.report_location_' + str(gcl_name[-1])
          gcl_name = gdp.GDP_NAME(logName)
          gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RA)
          # First parameter for evaluation purposes only, can be removed later.
          data = json.dumps(tmp_location)
          gcl_handle.append({'data': data})
            


      # Handling the location information reporting from invoked provisioning services
      elif 'report' in gcl_name:
        locations.append((tmp_request['timestamp'], tmp_request['location'], gcl_name))       

    # Don't handle NULL events
    except:
      break
  
  # Updating memorized requests if needed
  if len(mem_requests_old) > 0 or len(mem_requests) > 0:
    memorized_requests = update_memorized_requests(mem_requests_old, mem_requests)
    mem_requests_q.put(memorized_requests)

  # Signaling to other threads
  offering_q.put(offerings)
  request_q.put(requests)
  location_q.put(locations)
  return




def request_discovery(ils_id, services):
  """
    Discovery of provisioning features form the available provisioning services.

    ils_id - ID of this integrated location service, needed for shared provisioning services
    services - services whose provisioning features are to be requested
  """
  
  # Request features discovery
  for service_id in services:

    # Writing an entry to a 'service discovery' log of each requested provisioning service
    logName = 'lemic.localization.esi.service_discovery_' + str(service_id)
    gcl_name = gdp.GDP_NAME(logName)
    gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RA)
    data = json.dumps({'ils_id': ils_id})
    gcl_handle.append({'data': data})
  
  return




def query_for_location(requests, provisioning_features, ils_id, mapper_q):
  """
    Requesting location information provisioning from the selected provisioning services.

    requests - requests for location information by the applications
    provisioning_features - provisioning features of the available provisioning services
    ils_id - ID of this integrated location service, needed for shared provisioning services
    mapper_q - contains mapping between the requirements from the applications and the locations provided by the provisioning services
  """

  # This variable is used as a buffer for matching the requirements from the applications with the selected provisioning services.  
  memo = {}
  timestamp = float("{0:.2f}".format(time.time()))
  memo[timestamp] =  {}
  # Select provisioning services to be invoked
  #selected_services = SA.select_provisioning_services_prsa(requests, provisioning_features)    
  selected_services = SA.select_provisioning_services_ptsa(requests, provisioning_features)
  for sv in selected_services:
    memo[timestamp][sv] = {}
    memo[timestamp][sv]['elements'] = selected_services[sv]['elements']
    memo[timestamp][sv]['accuracy'] = selected_services[sv]['accuracy']
    # Evaluation purposes only, can be removed later
    memo[timestamp][sv]['timestamp_start'] = requests[sv]['timestamp_start']
  selected_ids = [selected_services[i]['elements'] for i in selected_services]
  selected_ids_final = list(set([val for sublist in selected_ids for val in sublist]))
  for id in selected_ids_final:
    logName = 'lemic.localization.esi.request_location_' + str(id[-1])
    gcl_name = gdp.GDP_NAME(logName)
    gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RA)
    data = json.dumps({'ils_id': ils_id, 'timestamp': timestamp})
    gcl_handle.append({'data': data})

  mapper_q.put(memo) 
  return




def merge_and_report_locations(location, mem, cashed_locations, cashed_locations_q):
  """
    Merging provided location information and reporting them to the applications based on their requirements
  
    location - contains all provided location information
    mem - contains mapping between the requirements from the applications and the locations provided by the provisioning services
    cashed_locations - current cashed locations 
    cashed_locations_q - queue containing cashed locations, used for multi-thread signaling
  """

  global memory
  memory = mem

  # Cleaning the memory buffer
  for num, mapp in enumerate(memory):
    if len(memory[num][memory[num].keys()[0]]) == 0:
      del memory[num] 

  for loc in location:
    for num, mapp in enumerate(memory):
      if loc[0] in mapp.keys():
        for key in mapp.keys():
          for key2 in mapp[key].keys():
            if 'lemic.localization.esi.service_offering_' + str(loc[2][-1]) in mapp[key][key2]['elements']:
              try:
                memory[num][key][key2]['locations'].append(loc[1])
              except:
                memory[num][key][key2]['locations'] = []
                memory[num][key][key2]['locations'].append(loc[1])

  to_remove = {}
  recent_locations = []
  for num, mapp in enumerate(memory):
    for key in mapp.keys():
      for key2 in mapp[key].keys(): 
        
        # This check is needed because memory is a global variable
        if 'locations' in mapp[key][key2]: 
          if len(mapp[key][key2]['elements']) == len(mapp[key][key2]['locations']):
                
            try:
              to_remove[key].append(key2)
            except:
              to_remove[key] = []
              to_remove[key].append(key2)

            # Calculate final location estimate
            final_est_x = 0.0
            final_est_y = 0.0
            list_room = []
            number_of_valid_locations = 0.0
            for entry in mapp[key][key2]['locations']:
              # Try/except to handle the possibility that locations reported by some provisioning services are 'None'.
              try:
                final_est_x += entry['est_coordinate_x']
                final_est_y += entry['est_coordinate_y']
                number_of_valid_locations += 1.0
              except:
                pass
              try:
                list_room.append(entry['est_room_label'])
              except:
                pass


            # To handle the case where all reported locations are 'None'
            try:
              final_est_x = final_est_x / number_of_valid_locations
              final_est_y = final_est_y / number_of_valid_locations
            except:
              final_est_x = None
              final_est_y = None
            try:
              final_room = most_common(list_room)
            except:
              final_room = None


            # Report locations to the applications based on their requirements
            logName = 'lemic.localization.sli.report_location_' + str(key2[-1])
            gcl_name = gdp.GDP_NAME(logName)
            gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RA)
            # First parameter for evaluation purposes only, can be removed later.
            data = json.dumps({'timestamp_start': mapp[key][key2]['timestamp_start'], 'est_coordinate_x': final_est_x, 'est_coordinate_y': final_est_y, 'est_room_label': final_room})
            gcl_handle.append({'data': data})
            recent_locations.append({'est_x': final_est_x, 'est_y': final_est_y, 'est_room': final_room, 'accuracy': mapp[key][key2]['accuracy'], 'location_type': None, 'timestamp': time.time()})
            cashed_locations = update_cashing(cashed_locations, recent_locations)

  cashed_locations_q.put(cashed_locations)
  # Remove that entry from the memory
  for num, mapp in enumerate(memory):
    for key in to_remove.keys():
        for item in to_remove[key]:
            try:
              del memory[num][key][item]
            except:
              pass 

  return




class App():


  def __init__(self):
    self.stdin_path = '/dev/null'
    self.stdout_path = '/dev/tty'
    self.stderr_path = '/dev/tty'
    self.pidfile_path = '/tmp/foo.pid'
    self.pidfile_timeout = 5


  def run(self):

    request_q = Queue()
    memorized_requests_q = Queue()
    offering_q = Queue()
    mapper_q = Queue()
    location_q = Queue()
    cashed_locations_q = Queue()
    requests = {}
    cashed_locations = []
    provisioning_features = {}
    memory = []
    location = []    
    ils_id = '1'
    gdp.gdp_init('localhost')
    
    # Get a list of registered provisioning services
    logName = 'lemic.localization.esi.register_service'
    gcl_name = gdp.GDP_NAME(logName)
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

    # Subscribe for capturing requests
    logs = ['lemic.localization.sli.request_location_1','lemic.localization.sli.request_location_2']
    obj_name_mapping = {}

    for name_str in logs:

      gcl_name = gdp.GDP_NAME(name_str)
      gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RO)
      obj_name_mapping[gcl_handle] = name_str
      gcl_handle.subscribe(0, 0, None)

    # Discover provisioning features
    # Subscribe to all service offering logs.
    for service_id in services:   # [services]   
      logName = 'lemic.localization.esi.service_offering_' + str(service_id)
      gcl_name = gdp.GDP_NAME(logName)
      gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RO)
      obj_name_mapping[gcl_handle] = logName
      gcl_handle.subscribe(0, 0, None)  

    # Subscribe to all service offering logs.
    for service_id in services:   # [services]   
      logName = 'lemic.localization.esi.report_location_' + str(service_id)
      gcl_name = gdp.GDP_NAME(logName)
      gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RO)
      obj_name_mapping[gcl_handle] = logName
      gcl_handle.subscribe(0, 0, None)  


    while True:
      """
      Implementation of the integrated location service.
      """

      t1 = Thread(target = read_logs, args = (obj_name_mapping, ils_id, cashed_locations, request_q, offering_q, location_q, memorized_requests_q))
      t2 = Thread(target = request_discovery, args = (ils_id, services,)) 
      t1.start()
      t2.start()

      if len(provisioning_features) > 0 and len(requests) > 0:
        # Make a selection decision
        t3 = Thread(target = query_for_location, args = (requests, provisioning_features, ils_id, mapper_q,))
        t3.start()

      if len(location) > 0:
        t4 = Thread(target = merge_and_report_locations, args=(location, memory, cashed_locations, cashed_locations_q,))
        t4.start() 
      
      newtime = time.time()
      requests = request_q.get()
      # for i in requests:
      #  requests[i]['request_time'] = newtime - requests[i]['request_time']
      provisioning_features = offering_q.get()
      
      
      try:
        tmp_mem = mapper_q.get_nowait()
        if tmp_mem:
          memory.append(tmp_mem)
      except:
        pass

      try:  
        location = location_q.get_nowait()
      except:
        pass

      try:  
        cashed_locations = cashed_locations_q.get_nowait()
      except:
        pass


def main():

  app = App()
  # This application is envisioned to be run as a daemon
  deamon_runner = runner.DaemonRunner(app)
  deamon_runner.do_action()

if __name__ == "__main__":
  main()
