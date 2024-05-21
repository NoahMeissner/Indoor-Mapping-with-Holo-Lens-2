# Copyright (c) Noah Meißner.
# Licensed under the MIT License.

import math
from Rotate import Rotate
import pandas as pd

'''
Class to generate corridor object
'''


def move_corridor(floor, name):
    try:
        point = floor[(floor['room'] == name) & (floor['type'] == 'Start')]
        x = point['x'].iloc[0]
        y = point['y'].iloc[0]
        floor['x'] -= x
        floor['y'] -= y
        return floor
    except Exception as e:
        print(f"move_corridor_error:{name} + error:{e}")


def get_name(floor, name):
    try:
        fil = floor[floor['room'] == name]
        return fil['corridor'].iloc[0]
    except Exception as e:
        print(f"get_name_error:{name} + error:{e}")


def get_max_nodes(ls):
    try:
        res = {}
        for corr in ls.keys():
            df = ls[corr].get_dataframe()
            rows, cols = df.shape
            res[corr] = rows
        return max(res, key=lambda key: res[key])
    except Exception as e:
        print(f"get_max_nodes Error:{e}")


def turn(df, end_point, vector_room, vector_floor):
    try:
        dot_product = (vector_room[1] * vector_floor[1]
                       + vector_room[0] * vector_floor[0])
        magnitude_a = math.sqrt(vector_room[1] ** 2 + vector_room[0] ** 2)
        magnitude_b = math.sqrt(vector_floor[1] ** 2 + vector_floor[0] ** 2)

        if magnitude_a == 0 or magnitude_b == 0:
            return df

        cosine_angle = dot_product / (magnitude_a * magnitude_b)
        if not -1 <= cosine_angle <= 1:
            return df

        angle = math.degrees(math.acos(cosine_angle))
        turn_object = Rotate(df)
        return turn_object.rotate_object(df, end_point, angle)
    except Exception as e:
        print(f'Turn Error: {e}')
        print(f'endpoint:{end_point},'
              + f' vector_room{vector_room},'
              + f' vector_floor{vector_floor}')
        return df


def check_turned(floor, room, room_name, floor_name):
    try:
        filtered_floor = floor[floor['room'] == room_name]
        filtered_room = room[room['room'] == floor_name]
        room_end = filtered_room[filtered_room['type'] == 'door'].iloc[0]
        floor_end = filtered_floor[filtered_floor['type'] == 'door'].iloc[0]
        return turn(room,
                    room_end,
                    [room_end['y'],
                     room_end['x']],
                    [floor_end['y'],
                     floor_end['x']])
    except Exception as e:
        print(f"check_turned Error:{e}")


def check_y_direction(room, room_name, floor_y_min, floor_y_max):
    filtered_room = room[(room['orig'] == 'init')
                         & (room['corridor'] == room_name)]
    try:
        if abs(floor_y_max) < abs(floor_y_min):
            # Condition 1 (Room should be above)
            zw = 0
            for i in filtered_room['y']:
                if i < floor_y_min:
                    room['y'] = -room['y']
                    return room
                elif i < floor_y_max:
                    zw += 1
            if zw > 4:
                room['y'] = -room['y']
                return room
            else:
                return room
        else:
            # Condition 2 (Room should be underneath)
            zw = 0

            for i in filtered_room['y']:
                if i > floor_y_max:
                    room['y'] = -room['y']
                    return room
                elif i > floor_y_min:
                    zw += 1
            if zw > 4:
                room['y'] = -room['y']
                return room
            else:
                return room
    except Exception as e:
        print(f"check_y_direction Error:{e}")


def check_x_direction(room, floor, room_number, floor_name):
    try:

        floor = floor[floor['room'] == room_number]
        room_door = room[room['room'] == floor_name]
        floor_start = floor[floor['type'] == 'Start'].iloc[0]
        floor_next = floor[floor['type'] == 'door'].iloc[0]
        room_start = room_door[room_door['type'] == 'Start'].iloc[0]
        room_end_door = room_door[room_door['type'] != 'Start'].iloc[0]

        vector_corridor = (floor_start['x'] - floor_next['x'])
        vector_room = (room_start['x'] - room_end_door['x'])

        both_positive = vector_corridor > 0 and vector_room > 0
        both_negative = vector_corridor < 0 and vector_room < 0

        if both_negative or both_positive:
            return room
        else:
            room['x'] = -room['x']
            return room
    except Exception as e:
        print(f"check_x_direction Error:{e}")


def add_corridors_together(floor, floor_room, floor_room_name):
    try:
        result = None
        floor_name = get_name(floor, floor_room_name)
        floor_room = move_corridor(floor_room, floor_name)
        floor = move_corridor(floor, floor_room_name)
        filtered_floor = floor[
            (floor['type'] == "corner")
            & (floor['corridor'] == floor_name)
            & (floor['orig'] == 'init')]
        if not filtered_floor.empty:
            floor_y_min = min(filtered_floor['y'])
            floor_y_max = max(filtered_floor['y'])
        else:
            print('floor empty')
            return
        floor_room = check_turned(floor,
                                  floor_room,
                                  floor_room_name,
                                  floor_name)
        floor_room = check_y_direction(floor_room,
                                       floor_room_name,
                                       floor_y_min,
                                       floor_y_max)
        floor_room = check_x_direction(floor_room,
                                       floor,
                                       floor_room_name,
                                       floor_name)
        if floor_room is not None:
            result = pd.concat([floor, floor_room], ignore_index=True)
        else:
            print('is not working : ' + floor_room_name + ":" + floor_name)
        return result
    except Exception as e:
        print(f"add_corridors_together Error:{e}")
        return None


class Corridor:

    def __init__(self, name, list_connections, dataframe):
        self.name = name
        self.conn = list_connections
        self.dataframe = dataframe

    def get_dataframe(self):
        return self.dataframe

    def set_dataframe(self, df):
        self.dataframe = df

    def get_name(self):
        return self.name

    def get_conn(self):
        return self.conn

    def set_conn(self, ls):
        self.conn = ls


class Combine:

    def __init__(self, corridor_list):
        self.corridor_list = corridor_list

    def combine(self):
        corridors = self.corridor_list
        object_list = {}
        for i in corridors.keys():
            conn = []
            df = corridors[i]
            for corr_name in corridors.keys():
                if corr_name in df['room'].tolist() and i != corr_name:
                    conn.append(corr_name)
            object_list[i] = (Corridor(i, conn, corridors[i]))

        main_corridor = get_max_nodes(object_list)
        main_corridor_object = object_list.get(main_corridor)
        agenda = main_corridor_object.get_conn()
        df = main_corridor_object.get_dataframe()
        df['corridor'] = main_corridor
        while len(agenda) > 0:
            for co in agenda:
                try:
                    if type(co) is list:
                        co = co[0]
                    co_object = object_list[co]
                    co_object_df = co_object.get_dataframe()
                    co_object_df['corridor'] = co
                    df = add_corridors_together(df, co_object_df, co)
                    if co in agenda:
                        agenda.remove(co)
                    else:
                        agenda.remove([co])
                    co_conn = co_object.get_conn()
                    if main_corridor in co_conn:
                        co_conn.remove(main_corridor)
                    else:
                        name = get_name(df, co)
                        co_conn.remove(name)
                    if co_conn is not None:
                        agenda.append(co_conn)
                except Exception as e:
                    print(f"combine Error: {e}")
                    break
            agenda = [agenda for agenda in agenda if agenda]
        return df
