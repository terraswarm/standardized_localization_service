#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Mapping of local coordinates to semantic (room-level) locations, and vice-versa.
"""

__author__ = "Filip Lemic"
__copyright__ = "Copyright 2017, EU eWine Project"

__version__ = "1.0.0"
__maintainer__ = "Filip Lemic"
__email__ = "lemic@tkn.tu-berlin.de"
__status__ = "Development"


def get_room(coord_x, coord_y):
    """
        Mapping of local coordinates to semantic (room-level) locations.

        arguments:
            - coord_x - x-coordinate of local location information
            - coord_y - y-coordinate of local location information

        returns:
            room label
    """

    if coord_x >= 0.0     and coord_x < 3.25   and coord_y >= 0.0  and coord_y < 6.72:
        return  'FT222'
    elif coord_x >= 3.25  and coord_x < 9.42   and coord_y >= 0.0  and coord_y < 6.72:
        return 'FT223'
    elif coord_x >= 9.42  and coord_x < 15.67  and coord_y >= 0.0  and coord_y < 6.72:
        return 'FT224'
    elif coord_x >= 15.67 and coord_x < 21.16  and coord_y >= 0.0  and coord_y < 6.72:
        return 'FT225'
    elif coord_x >= 21.16 and coord_x <= 30.87 and coord_y >= 0.0  and coord_y < 6.72:
        return 'FT226'
    elif coord_x >= 0.0   and coord_x < 13.0   and coord_y >= 6.72 and coord_y < 8.89:
        return 'hollway_2nd_west'
    elif coord_x >= 13.0  and coord_x < 25.19  and coord_y >= 6.72 and coord_y < 8.89:
        return 'hollway_2nd_west'
    elif coord_x >= 25.19 and coord_x <= 30.87 and coord_y >= 6.72 and coord_y <= 15.56:
        return 'stairs_2nd'
    elif coord_x > 0.0    and coord_x < 3.21   and coord_y >= 8.89 and coord_y <= 15.56:
        return 'FT236'
    elif coord_x >= 3.31  and coord_x < 6.42   and coord_y >= 8.89 and coord_y <= 15.56:
        return 'FT235'
    elif coord_x >= 6.42  and coord_x < 12.65  and coord_y >= 8.89 and coord_y <= 15.56:
        return 'FT234' 
    elif coord_x >= 12.65 and coord_x < 15.93  and coord_y >= 8.89 and coord_y <= 15.56:
        return 'FT233'
    elif coord_x >= 15.93 and coord_x < 19.12  and coord_y >= 8.89 and coord_y <= 15.56:
        return 'FT232'
    elif coord_x >= 19.12 and coord_x < 22.12  and coord_y >= 8.89 and coord_y <= 15.56:
        return 'FT231'
    elif coord_x >= 22.12 and coord_x < 25.19  and coord_y >= 8.89 and coord_y <= 15.56:
        return 'FT230'
    return 'no_room'


def get_coordinate(room_label):
        """
        Mapping of semantic (room-level) locations to local coordinates.

        arguments:
            room label

        returns:
            tuple (coord_x, coord_y)
            - coord_x - x-coordinate of local location information
            - coord_y - y-coordinate of local location information
    """

    if room_label == "FT222":
        return (2.1, 3.6)
    elif room_label == "FT233":
        return (14.1, 12.4)
    elif room_label == "FT232":
        return (17.1, 12.4)
    elif room_label == "FT231":
        return (20.7, 12.4)
    elif room_label == "FT223":
        return (6.6, 3.6)
    elif room_label == "FT224":
        return (12.9, 3.6)
    elif room_label == "FT225":
        return (19.1, 3.6)
    elif room_label == "hallway_west":
        return (6.9, 9.0)
    elif room_label == "hallway_east":
        return (19.1, 9.0)
    elif room_label == "FT236":
        return (2.1, 12.4)
    elif room_label == "FT235":    
        return (5.4, 12.4)
    elif room_label == "FT234":
        return (9.8, 12.4)
    return (None, None)

