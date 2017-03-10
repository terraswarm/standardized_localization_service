#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
	Algorithms for selection of location information provisioning services based on the requirements from the 
	location-based applications and provisioning features of available location information provisioning services.
"""

__author__ = "Filip Lemic"
__copyright__ = "Copyright 2017, EU eWine Project"

__version__ = "1.0.0"
__maintainer__ = "Filip Lemic"
__email__ = "lemic@tkn.tu-berlin.de"
__status__ = "Development"


import itertools
import collections
import numpy, math
import pprint


def combine(combination_input):
  """
    Help function for providing all combinations of provisioning services.
	
	arguments:
    	combination_input - list of all services for creating the combinations

    returns:
    	ordered combinations of provisioning services
  """

  output = sum([map(list, itertools.combinations(combination_input, i)) for i in range(len(combination_input) + 1)], [])
  output_final = [sorted(i) for i in output if len(i)>1]

  return sorted(output_final)


flatten = lambda *n: (e for a in n for e in (flatten(*a) if isinstance(a, (tuple, list)) else (a,)))


def generate_virtual_services(offering, error_tr):
  """
    Read the paper for more details. The idea is to match provisioning services with similar provisioning features 
    into virtual provisioning services with enhanced accuracy.

	arguments:
    	offering - all current offerings
    	error_tr - threshold for the accuracy similarity

	returns:
		virtual location information provisioning services
  """
  
  # Temporary variables used for calculating provisioning features of virtual provisioning services.
  accuracy = {}
  latency = {}
  power = {}

  # Return variable- specification of the virtual provisioning services.
  offer = {}

  # Initial provisioning services are real provisioning services - mapping 1 to 1.
  for iterator, key in enumerate(offering):
    offer[iterator]                      = {}
    offer[iterator]['accuracy']          = offering[key]['accuracy']
    offer[iterator]['latency']           = offering[key]['latency']
    offer[iterator]['power_consumption'] = offering[key]['power_consumption']
    offer[iterator]['elements']          = [key]
    accuracy[key] = offering[key]['accuracy']
    latency[key]  = offering[key]['latency']
    power[key]    = offering[key]['power_consumption']
    
  # Combine services with similar accuracy - based on accuracy threshold error_tr
  final_virtual_services = []
  for key1 in accuracy:
    combination_input = []
    combination_input.append(key1)
    for key2 in accuracy:
      if key1 != key2 and abs(accuracy[key1] - accuracy[key2]) < error_tr:
        combination_input.append(key2)

    if len(combination_input) > 1:
      final_virtual_services.append(combine(combination_input))

  final_virtual_services = list(itertools.chain.from_iterable(final_virtual_services))
  final_virtual_services = [list(t) for t in set(map(tuple, final_virtual_services))]

  # Calculate provisioning features for the added virtual services. 
  iterator += 1
  if all(isinstance(i, list) for i in final_virtual_services):
    for combo in final_virtual_services:  
      offer[iterator] = {}
      offer[iterator]['accuracy'] = numpy.mean([accuracy[i] for i in combo])/math.sqrt(len(combo))
      offer[iterator]['latency'] = numpy.max([latency[i] for i in combo])
      offer[iterator]['power_consumption'] = numpy.sum([power[i] for i in combo])
      offer[iterator]['elements'] = combo 
      iterator += 1
  elif len(final_virtual_services) > 1:
    offer[iterator] = {}
    offer[iterator]['accuracy'] = numpy.mean([accuracy[i] for i in final_virtual_services])/math.sqrt(len(final_virtual_services))
    offer[iterator]['latency'] = numpy.max([latency[i] for i in final_virtual_services])
    offer[iterator]['power_consumption'] = numpy.sum([power[i] for i in final_virtual_services])
    offer[iterator]['elements'] = list(final_virtual_services)
    iterator += 1

  return offer




def select_provisioning_services_prsa(requirements, offerings, error_tr = 0.15):
  """
    Per request based selection of provisioning services based on the requirements from the applications
    and offerings from the available location information provisioning services.

	arguments:
    	requirements - current requirements for location information from the applications
    	offerings - current offerings (provisioning features) from provisioning services
    	error_tr - threshold for the accuracy similarity

	returns:
		location information provisioning services to be invoked for generating location information
  """

  # Generate virtual services
  virtual_offerings = generate_virtual_services(offerings, error_tr)
  # Defining arrival specification.
  latency_req = {}

  for i in requirements:
    latency_req[i]  = requirements[i]['period'] - requirements[i]['request_time']

  # Sort by request time
  latency_req_sorted = collections.OrderedDict(sorted(latency_req.items(), key=lambda t: t[1]))

  decision = {}
  for key, value in latency_req_sorted.items():
    flag = 0
    decision[key] = {}
    for virtual_offering in virtual_offerings:
      if virtual_offerings[virtual_offering]['accuracy'] < requirements[key]['accuracy'] and virtual_offerings[virtual_offering]['latency'] < requirements[key]['period'] - requirements[key]['request_time']:
        if flag == 0:
          decision[key]['key'] = virtual_offering
          decision[key]['accuracy'] = virtual_offerings[virtual_offering]['accuracy']
          decision[key]['latency'] = virtual_offerings[virtual_offering]['latency']
          decision[key]['elements'] = virtual_offerings[virtual_offering]['elements']
          decision[key]['power_consumption'] = virtual_offerings[virtual_offering]['power_consumption']  
          flag = 1
        elif decision[key]['power_consumption'] > virtual_offerings[virtual_offering]['power_consumption']:
          decision[key]['key'] = virtual_offering
          decision[key]['accuracy'] = virtual_offerings[virtual_offering]['accuracy']
          decision[key]['latency'] = virtual_offerings[virtual_offering]['latency']
          decision[key]['elements'] = virtual_offerings[virtual_offering]['elements']
          decision[key]['power_consumption'] = virtual_offerings[virtual_offering]['power_consumption']  
    
    try:
      len(virtual_offerings[decision[key]['key']])
    except:
      for virtual_offering in virtual_offerings:
        if virtual_offerings[virtual_offering]['latency'] < requirements[key]['period'] - requirements[key]['request_time']:
          if flag == 0:
            decision[key]['key'] = virtual_offering
            decision[key]['accuracy'] = virtual_offerings[virtual_offering]['accuracy']
            decision[key]['latency'] = virtual_offerings[virtual_offering]['latency']
            decision[key]['elements'] = virtual_offerings[virtual_offering]['elements']
            decision[key]['power_consumption'] = virtual_offerings[virtual_offering]['power_consumption']  
            flag = 1
          elif decision[key]['accuracy'] > virtual_offerings[virtual_offering]['accuracy']:
            decision[key]['key'] = virtual_offering
            decision[key]['accuracy'] = virtual_offerings[virtual_offering]['accuracy']
            decision[key]['latency'] = virtual_offerings[virtual_offering]['latency']
            decision[key]['elements'] = virtual_offerings[virtual_offering]['elements']
            decision[key]['power_consumption'] = virtual_offerings[virtual_offering]['power_consumption']  
      try:
        len(virtual_offerings[decision[key]['key']])
      except:
        for virtual_offering in virtual_offerings:
          if flag == 0:
            decision[key]['key'] = virtual_offering
            decision[key]['accuracy'] = virtual_offerings[virtual_offering]['accuracy']
            decision[key]['latency'] = virtual_offerings[virtual_offering]['latency']
            decision[key]['elements'] = virtual_offerings[virtual_offering]['elements']
            decision[key]['power_consumption'] = virtual_offerings[virtual_offering]['power_consumption']  
            flag = 1
          elif decision[key]['latency'] > virtual_offerings[virtual_offering]['latency']:
            decision[key]['key'] = virtual_offering
            decision[key]['accuracy'] = virtual_offerings[virtual_offering]['accuracy']
            decision[key]['latency'] = virtual_offerings[virtual_offering]['latency']
            decision[key]['elements'] = virtual_offerings[virtual_offering]['elements']
            decision[key]['power_consumption'] = virtual_offerings[virtual_offering]['power_consumption']  


  pprint.pprint(decision)
  return decision




def make_decision_min_power(possible_services, offerings):
	"""
		finding a decision with minimized power consumption. 

		arguments:
			- possible_services - possible services to be invoked
			- offerings - features of provisioning services

		returns:
			decision with minimal power consumption
	"""

	flag = 0
	for i in possible_services:
		if flag == 0:
			decision = list(possible_services[i])
			flag = 1
		else:
			decision = list(itertools.product(decision, possible_services[i]))

	flat_decision = []
	power = []
	for i in decision:
		services = list(set(list(flatten(i))))
		if services not in flat_decision:
			flat_decision.append(services)
			power_one = 0
			for service in services:
				#print service
				power_one += offerings[service]['power_consumption']
			power.append(power_one)
	index_min = min(xrange(len(power)), key=power.__getitem__)

	return flat_decision[index_min]





def select_provisioning_services_ptsa(requirements, offerings, error_tr = 0.15):
	"""
    Per time-bucket based selection of provisioning services based on the requirements from the applications
    and offerings from the available location information provisioning services.

	arguments:
    	requirements - current requirements for location information from the applications
    	offerings - current offerings (provisioning features) from provisioning services
    	error_tr - threshold for the accuracy similarity

	returns:
		location information provisioning services to be invoked for generating location information
	"""

	# Generate virtual services
	virtual_offerings = generate_virtual_services(offerings, error_tr)

	# Defining (acc, lat) requirements for the whole bucket.
	accuracy_req = {}
	latency_req = {}

	# Specify variables accuracy and latency-req_time
	for i in requirements:
		accuracy_req[i] = requirements[i]['accuracy']
		latency_req[i]  = requirements[i]['period'] - requirements[i]['request_time']

	# Sort by latency
	latency_req_sorted = collections.OrderedDict(sorted(latency_req.items(), key=lambda t: t[1]))

	# Find the highest accuracy requirement
	acc_req_key = min(accuracy_req, key=accuracy_req.get)
	# Find the highest latency requirement
	lat_first_key = latency_req_sorted.keys()[0]

	# Algorithm execution, specification of the final requirements (reduction of requirements)
	requirements_final  = []
	while True:

		new_accuracy = {}
		for key, value in latency_req_sorted.items():

			if acc_req_key != key:
				new_accuracy[key] = accuracy_req[key]
			else:
				break

		requirements_final.append((acc_req_key, accuracy_req[acc_req_key], latency_req[acc_req_key]))

		try:
			acc_req_key = min(new_accuracy, key=new_accuracy.get)
		except:
			break

	# Specification of unions of possible elementary services to meet the requirements
	possible_services = {}
	for requirement in requirements_final:
		possible_services[requirement[0]] = []

		for key in virtual_offerings:

			if virtual_offerings[key]['accuracy'] < requirement[1] and virtual_offerings[key]['latency'] < requirement[2]:

				possible_services[requirement[0]].append(virtual_offerings[key]['elements'])

		# In case there are no services available that will meet the requirements - don't 
		# focus on power minimization in that case
		if len(possible_services[requirement[0]]) == 0:

			# If there are multiple services that meet the latency requirement, find the best accuracy
			flag = 0
			for key in virtual_offerings:
				if flag == 0:
					smallest_latency = (key, virtual_offerings[key]['latency'])
					flag = 1
				elif virtual_offerings[key]['latency'] < smallest_latency[1]:
					smallest_latency = (key, virtual_offerings[key]['latency'])

			possible_alternatives = {}
			for key in virtual_offerings:
				if virtual_offerings[key]['latency'] < requirement[2]:
					possible_alternatives[key] = virtual_offerings[key]['accuracy']

			# If none of the services meet the latency requirement, use the closest one to the latency requirement
			if len(possible_alternatives) != 0:
				key = min(possible_alternatives, key=possible_alternatives.get)
				possible_services[requirement[0]].append(virtual_offerings[key]['elements'])
			else:
				possible_services[requirement[0]].append(virtual_offerings[smallest_latency[0]]['elements'])

	decision_tmp = make_decision_min_power(possible_services, offerings)

	services = {}
	for i in decision_tmp:
		services[i] = {}
		services[i]['accuracy'] = offerings[i]['accuracy']
		services[i]['latency'] = offerings[i]['latency']
		services[i]['power_consumption'] = offerings[i]['power_consumption']
		services[i]['elements'] = offerings[i]['elements']

	virtual_tmp = generate_virtual_services(services, error_tr)

	power_min = None
	power_exp = virtual_tmp[0]['power_consumption']
	decision = {}
	for i in requirements:
		for j in virtual_tmp:
			if requirements[i]['accuracy'] < virtual_tmp[j]['accuracy'] and requirements[i]['period'] < virtual_tmp[j]['latency'] and power_exp > virtual_tmp[j]['power_consumption']:
				power_min = j
				power_exp = virtual_tmp[j]['power_consumption']
			
		if power_min is None:
			accuracy = None
			for j in virtual_tmp:
				if requirements[i]['period'] < virtual_tmp[j]['latency']:
					if accuracy is None or accuracy > virtual_tmp[j]['accuracy']:
						accuracy_index = j
						accuracy = virtual_tmp[j]['accuracy']
					
			if accuracy is None:
				latency_key = 0
				latency_exp = virtual_tmp[0]['latency']
				for j in virtual_tmp:
					if latency_exp > virtual_tmp[j]['latency']:
						latency_key = j

				decision[i] = {}
				decision[i]['key'] = i
				decision[i]['accuracy'] = virtual_tmp[latency_key]['accuracy']
				decision[i]['latency'] = virtual_tmp[latency_key]['latency']
				decision[i]['elements'] = virtual_tmp[latency_key]['elements']
				decision[i]['power_consumption'] = virtual_tmp[latency_key]['power_consumption']

			else:
				decision[i] = {}
				decision[i]['key'] = i
				decision[i]['accuracy'] = virtual_tmp[accuracy_index]['accuracy']
				decision[i]['latency'] = virtual_tmp[accuracy_index]['latency']
				decision[i]['elements'] = virtual_tmp[accuracy_index]['elements']
				decision[i]['power_consumption'] = virtual_tmp[accuracy_index]['power_consumption']

		else:
			decision[i] = {}
			decision[i]['key'] = i
			decision[i]['accuracy'] = virtual_tmp[power_min]['accuracy']
			decision[i]['latency'] = virtual_tmp[power_min]['latency']
			decision[i]['elements'] = virtual_tmp[power_min]['elements']
			decision[i]['power_consumption'] = virtual_tmp[power_min]['power_consumption']

	return decision