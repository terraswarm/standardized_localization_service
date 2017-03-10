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


from scipy.stats.mstats import mquantiles
import numpy as np
from os import listdir
from os.path import isfile, join



def get_training_files(path):
    
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]

    return onlyfiles



def read_file_euclidean(file):
    
    with open(file) as f:
        content = f.readlines()
        if content not in ('\n', '\r\n'):
            training_point = {}
            training_point['id'] = int(content[0].split(',')[0])
            try:
                training_point['room_label']   = str(content[0].split(',')[3][:-1])
                training_point['coordinate_x'] = float(content[0].split(',')[1])
                training_point['coordinate_y'] = float(content[0].split(',')[2])
            except:
                training_point['room_label']   = str(content[0].split(',')[1][:-1])

            training_point['data'] = {}
            for i in content[1:]:
                training_point['data'][str(i.split(',')[0])] = float(i.split(',')[1][:-1])
        else:
            return None
    return training_point



def read_file_quantile(file):
    
    with open(file) as f:
        content = f.readlines()
        if content not in ('\n', '\r\n'):
            training_point = {}
            training_point['id'] = int(content[0].split(',')[0])
            training_point['coordinate_x'] = float(content[0].split(',')[1])
            training_point['coordinate_y'] = float(content[0].split(',')[2])
            training_point['room_label']   = str(content[0].split(',')[3][:-1])
            training_point['data'] = {}
            for i in content[1:]:
                training_point['data'][str(i.split(',')[0])] = [float(i.split(',')[1]), float(i.split(',')[2]), float(i.split(',')[3]), float(i.split(',')[4][:-1])]
        else:
            return None
    return training_point



def most_common(lst):
    """   """
    return max(set(lst), key=lst.count)



def getPositionEstimateQuantile(fingerprint, training_dataset_path):
    

    metric_ref = {}
    estimated_position_label = {}
    
    metric_ref[0] = 0
    metric_ref[1] = 0
    metric_ref[2] = 0

    estimated_position_label[0] = '0'
    estimated_position_label[1] = '0'
    estimated_position_label[2] = '0'

    training_files = get_training_files(training_dataset_path)
    coordinates = {}

    for training_file in training_files:
        training_point = read_file_quantile(training_dataset_path + training_file)
        if training_point != None:
            coordinates[training_point['id']] = {}
            try:
                coordinates[training_point['id']]['coordinate_x'] = training_point['coordinate_x']
                coordinates[training_point['id']]['coordinate_y'] = training_point['coordinate_y']
            except:
                pass
            coordinates[training_point['id']]['room_label'] = training_point['room_label']

            metric = 0
            training_data = {}

            key_list = [fingerprint[0].keys(), fingerprint[1].keys(), fingerprint[2].keys(), fingerprint[3].keys()]
            flatten_key_list = np.unique([val for sublist in key_list for val in sublist])
           
            for key in flatten_key_list:
                fingerpr_final = []
                try:
                    fingerpr_final.append(fingerprint[0][key]['rssi'])
                except:
                    pass
                try:
                    fingerpr_final.append(fingerprint[1][key]['rssi'])
                except:
                    pass
                try:
                    fingerpr_final.append(fingerprint[2][key]['rssi'])
                except:
                    pass
                try:
                    fingerpr_final.append(fingerprint[3][key]['rssi'])
                except:
                    pass
                if key in training_point['data'].keys():
                    metric += abs(np.linalg.norm(np.array(mquantiles(fingerpr_final, [0, 0.33, 0.67, 1])) - np.array(training_point['data'][key])))
                else:       
                    metric += abs(np.linalg.norm(np.array(mquantiles(fingerpr_final, [0, 0.33, 0.67, 1])) - np.array(mquantiles(-100, [0, 0.33, 0.67, 1]))))


            if metric_ref[0] == 0: 
                metric_ref[0] = metric
                estimated_position_label[0] = training_point['id']
            elif metric_ref[1] == 0:
                metric_ref[1] = metric
                estimated_position_label[1] = training_point['id']
            elif metric_ref[2] == 0:
                metric_ref[2] = metric
                estimated_position_label[2] = training_point['id']

            else:
                if metric < metric_ref[0]:
                    metric_ref[2] = metric_ref[1]
                    metric_ref[1] = metric_ref[0]
                    metric_ref[0] = metric
                    estimated_position_label[2] = estimated_position_label[1]
                    estimated_position_label[1] = estimated_position_label[0]
                    estimated_position_label[0] = training_point['id']
                elif metric < metric_ref[1]:
                    metric_ref[2] = metric_ref[1]
                    metric_ref[1] = metric
                    estimated_position_label[2] = estimated_position_label[1]
                    estimated_position_label[1] = training_point['id']
                elif metric < metric_ref[2]:
                    metric_ref[2] = metric
                    estimated_position_label[2] = training_point['id']

    coord_x = []
    coord_y = []
    room = []

    for i in estimated_position_label.values():
        try:
            coord_x.append(coordinates[i]['coordinate_x'])
            coord_y.append(coordinates[i]['coordinate_y'])
        except:
            pass
        room.append(coordinates[i]['room_label'])
        
    estimated_position = {}
    try:
        estimated_position['est_coordinate_x'] = (1.0/3)*coord_x[0] + (1.0/3)*coord_x[1] + (1.0/3)*coord_x[2]
        estimated_position['est_coordinate_y'] = (1.0/3)*coord_y[0] + (1.0/3)*coord_y[1] + (1.0/3)*coord_y[2]
    except:
        pass
    estimated_position['est_room_label'] = most_common(room)
    
    return estimated_position




def getPositionEstimateEuclidean(fingerprint, training_dataset_path):

    metric_ref = {}
    estimated_position_label = {}
    
    metric_ref[0] = 0
    metric_ref[1] = 0
    metric_ref[2] = 0

    estimated_position_label[0] = '0'
    estimated_position_label[1] = '0'
    estimated_position_label[2] = '0'

    training_files = get_training_files(training_dataset_path)
    coordinates = {}

    for training_file in training_files:
        training_point = read_file_euclidean(training_dataset_path + training_file)
        if training_point != None:
            coordinates[training_point['id']] = {}
            try:
                coordinates[training_point['id']]['coordinate_x'] = training_point['coordinate_x']
                coordinates[training_point['id']]['coordinate_y'] = training_point['coordinate_y']
            except:
                pass
            coordinates[training_point['id']]['room_label'] = training_point['room_label']

            metric = 0
            training_data = {}

            for key in fingerprint.keys():
                if key in training_point['data'].keys():
                    metric += np.absolute(fingerprint[key]['rssi'] - training_point['data'][key])
                else:
                    metric += np.absolute(fingerprint[key]['rssi'] + 100)

            if metric_ref[0] == 0: 
                metric_ref[0] = metric
                estimated_position_label[0] = training_point['id']
            elif metric_ref[1] == 0:
                metric_ref[1] = metric
                estimated_position_label[1] = training_point['id']
            elif metric_ref[2] == 0:
                metric_ref[2] = metric
                estimated_position_label[2] = training_point['id']

            else:
                if metric < metric_ref[0]:
                    metric_ref[2] = metric_ref[1]
                    metric_ref[1] = metric_ref[0]
                    metric_ref[0] = metric
                    estimated_position_label[2] = estimated_position_label[1]
                    estimated_position_label[1] = estimated_position_label[0]
                    estimated_position_label[0] = training_point['id']
                elif metric < metric_ref[1]:
                    metric_ref[2] = metric_ref[1]
                    metric_ref[1] = metric
                    estimated_position_label[2] = estimated_position_label[1]
                    estimated_position_label[1] = training_point['id']
                elif metric < metric_ref[2]:
                    metric_ref[2] = metric
                    estimated_position_label[2] = training_point['id']

    coord_x = []
    coord_y = []
    room = []

    for i in estimated_position_label.values():
        try:
            coord_x.append(coordinates[i]['coordinate_x'])
            coord_y.append(coordinates[i]['coordinate_y'])
        except:
            pass
        room.append(coordinates[i]['room_label'])

    estimated_position = {}
    try:
        estimated_position['est_coordinate_x'] = (1.0/3)*coord_x[0] + (1.0/3)*coord_x[1] + (1.0/3)*coord_x[2]
        estimated_position['est_coordinate_y'] = (1.0/3)*coord_y[0] + (1.0/3)*coord_y[1] + (1.0/3)*coord_y[2]
    except:
        estimated_position['est_coordinate_x'] = None
        estimated_position['est_coordinate_y'] = None
    estimated_position['est_room_label'] = most_common(room)
    
    return estimated_position