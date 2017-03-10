#!/bin/bash
stop="stop"
action=$1
if [ "$action" = "$stop" ]; then
	initial_string='python /home/tkn/Desktop/standardized_location_service/provisioning_services/provisioning_service_join_euclidean.py ' 
	string=$initial_string$action
	xterm -hold -e $string &	
	sleep 1
	initial_string='python /home/tkn/Desktop/standardized_location_service/provisioning_services/provisioning_service_join_quantile.py ' 
	string=$initial_string$action
	xterm -hold -e $string &
	sleep 1
	initial_string='python /home/tkn/Desktop/standardized_location_service/provisioning_services/provisioning_service_large_euclidean.py ' 
	string=$initial_string$action
	xterm -hold -e $string &
	sleep 1
	initial_string='python /home/tkn/Desktop/standardized_location_service/provisioning_services/provisioning_service_large_quantile.py ' 
	string=$initial_string$action
	xterm -hold -e $string &
	sleep 1
	initial_string='python /home/tkn/Desktop/standardized_location_service/provisioning_services/provisioning_service_small_euclidean.py ' 
	string=$initial_string$action
	xterm -hold -e $string &
	sleep 1
	initial_string='python /home/tkn/Desktop/standardized_location_service/provisioning_services/provisioning_service_small_quantile.py ' 
	string=$initial_string$action
	xterm -hold -e $string &
	sleep 1
	initial_string='python /home/tkn/Desktop/standardized_location_service/provisioning_services/provisioning_service_semantic_euclidean.py ' 
	string=$initial_string$action
	xterm -hold -e $string &
	sleep 1
	initial_string='python /home/tkn/Desktop/standardized_location_service/provisioning_services/provisioning_service_semantic_quantile.py ' 
	string=$initial_string$action
	xterm -hold -e $string &
	sleep 1
	killall xterm
else
	initial_string='python /home/tkn/Desktop/standardized_location_service/provisioning_services/provisioning_service_join_euclidean.py ' 
	string=$initial_string$action 
	xterm -hold -e $string &
	sleep 1		
	initial_string='python /home/tkn/Desktop/standardized_location_service/provisioning_services/provisioning_service_join_quantile.py ' 
	string=$initial_string$action
	xterm -hold -e $string &
	sleep 1
	initial_string='python /home/tkn/Desktop/standardized_location_service/provisioning_services/provisioning_service_large_euclidean.py ' 
	string=$initial_string$action
	xterm -hold -e $string &
	sleep 1
	initial_string='python /home/tkn/Desktop/standardized_location_service/provisioning_services/provisioning_service_large_quantile.py ' 
	string=$initial_string$action
	xterm -hold -e $string &
	sleep 1
	initial_string='python /home/tkn/Desktop/standardized_location_service/provisioning_services/provisioning_service_small_euclidean.py ' 
	string=$initial_string$action
	xterm -hold -e $string &
	sleep 1
	initial_string='python /home/tkn/Desktop/standardized_location_service/provisioning_services/provisioning_service_small_quantile.py ' 
	string=$initial_string$action
	xterm -hold -e $string &
	sleep 1
	initial_string='python /home/tkn/Desktop/standardized_location_service/provisioning_services/provisioning_service_semantic_euclidean.py ' 
	string=$initial_string$action
	xterm -hold -e $string &
	sleep 1
	initial_string='python /home/tkn/Desktop/standardized_location_service/provisioning_services/provisioning_service_semantic_quantile.py ' 
	string=$initial_string$action
	xterm -hold -e $string & 
	sleep 1
fi
