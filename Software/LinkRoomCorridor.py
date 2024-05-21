# Copyright (c) Noah Meißner.
# Licensed under the MIT License.

import pandas as pd

"""
This file connects rooms with corridors and later
returns a list of corridors with added corridors.
and later returns a list of corridors.
"""

"""
This Method will check if the y Direction is correct.
Because it can be the case, that the room is
horizontally mirrored
"""


def validate_horizontal_alignment(room, floor_y_min, floor_y_max):
    if abs(floor_y_max) < abs(floor_y_min):
        # Condition 1 (Room is above corridor)
        zw = 0
        for coordinate in room['y']:
            if coordinate < floor_y_min:
                room['y'] = -room['y']
                return room
            elif coordinate < floor_y_max:
                zw += 1
        if (zw / len(room['y'].tolist())) > 0.5:
            room['y'] = -room['y']
            return room
        else:
            return room
    else:
        # Condition 2 (Room is below corridor)
        zw = 0
        for coordinate in room['y']:
            if coordinate > floor_y_max:
                room['y'] = -room['y']
                return room
            elif coordinate > floor_y_min:
                zw += 1
        if (zw / len(room['y'].tolist())) > 0.5:
            room['y'] = -room['y']
            return room
        else:
            return room


"""
    This Method will check if the x Direction is correct
"""


def validate_vertical_alignment(room, floor, room_number):
    corridor = floor[floor['room'] == room_number]
    floor_start = corridor[corridor['type'] == 'Start'].iloc[0]
    floor_next = corridor[corridor['type'] == 'door'].iloc[0]

    room_start = room[room['type'] == 'Start'].iloc[0]
    room_end_door = room.tail(1)
    vector_corridor = (floor_start['x'] - floor_next['x'])
    vector_room = (room_start['x'] - room_end_door['x'].values[0])

    both_positive = vector_corridor > 0 and vector_room > 0
    both_negative = vector_corridor < 0 and vector_room < 0

    if both_negative or both_positive:
        return room
    else:
        room['x'] = -room['x']
        return room


'''
This method will move graph to start point,
so that we are able to add room to corridor
'''


def move(room, name):
    if name is None:
        point = room[room['type'] == 'Start']
    else:
        point = room[(room['room'] == name) & (room['type'] == 'Start')]
    x = point['x'].iloc[0]
    y = point['y'].iloc[0]
    room['x'] -= x
    room['y'] -= y
    return room


'''
Deals with one room and will connect both
'''


def add_rooms_together(floor, room, room_name):
    try:
        room = move(room, None)
        floor = move(floor, room_name)
        floor_y_min = min(floor[(floor['type'] == "corner")
                                & (floor['orig'] == 'init')]['y'])
        floor_y_max = max(floor[(floor['type'] == "corner")
                                & (floor['orig'] == 'init')]['y'])

        room = validate_horizontal_alignment(room, floor_y_min, floor_y_max)
        room = validate_vertical_alignment(room, floor, room_name)
        room['orig'] = 'room'

        result = pd.concat([floor, room], ignore_index=True)
        result = result[~((result['room'] == room_name)
                          & (result['orig'] == 'init'))]
        return result
    except Exception as e:
        print(e)


'''
Deals with all rooms and find match between room and corridor
'''


def add_room(room_list, floor):
    floor['orig'] = 'init'
    if floor is not None:
        for x, room in enumerate(room_list):
            filtered = room['room']
            if floor is not None:
                filtered_corridor = floor['room']
                if not filtered.empty and not filtered_corridor.empty:
                    if room['room'].iloc[0] in floor['room'].tolist():
                        room_name = str(room['room'].iloc[0]).strip()
                        floor = add_rooms_together(floor, room, room_name)
                else:
                    print("None")
    return floor


'''
This class will create from several dataframes a single frame
and add the rooms in the right place
'''


class Graph:
    """
    Constructor
    """

    def __init__(self, DataFrame_list):
        self.list_df = DataFrame_list

    '''
    SELECT Corridors and Rooms separately
    '''

    def select(self, corridor):
        list_line = []
        for x, list_n in enumerate(self.list_df):
            if corridor and not list_n[list_n['type'] == 'Init'].empty:
                list_line.append(list_n)
            elif not corridor and list_n[list_n['type'] == 'Init'].empty:
                list_line.append(list_n)
        return list_line

    '''
    This method is called to get the plans
    '''

    def get_plan(self):
        corridors_list = self.select(True)
        room_list = self.select(False)

        if len(corridors_list) < 1:
            print("error")
            return None

        else:
            res_list = {}
            for i in corridors_list:
                corridor_name = i[i['type'] == 'Init']['room'].iloc[0]
                res_list[corridor_name] = add_room(room_list, i)
            return res_list
