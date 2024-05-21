# Copyright (c) Noah Meißner.
# Licensed under the MIT License.

"""
This class facilitates the rotation of a surveyed
space for its subsequent utilization.
"""
import math
import numpy as np


def calculate_angle_dot_product(x_b, y_b):
    try:
        """
        Calculate the angle between two vectors A and B using the dot product.
        The vectors are defined by their coordinates (x_a, y_a) and (x_b, y_b).
        The angle is returned in degrees.
        """
        # Vector
        x = 1
        y = 0

        dot_product = x * x_b + y * y_b

        magnitude_a = math.sqrt(x ** 2 + y ** 2)
        magnitude_b = math.sqrt(x_b ** 2 + y_b ** 2)

        if magnitude_b == 0:
            return 0

        cos_angle = dot_product / (magnitude_a * magnitude_b)

        angle_rad = math.acos(cos_angle)
        angle_deg = math.degrees(angle_rad)
        return angle_deg
    except Exception as e:
        print(f"calculate_angle_dot_product Error:{e}")


def get_nodes(dataframe):
    filtered = dataframe[dataframe['type'] == 'corner']
    points = filtered.nsmallest(2, 'y')
    start = points.iloc[0]
    end = points.tail(1)
    return [start, end]


def validate_rotation(dataframe):
    filtered = dataframe[dataframe['type'] == 'corner']

    y_min_points = filtered[filtered['y'] == filtered['y'].min()]
    y_max_points = filtered[filtered['y'] == filtered['y'].max()]

    if not y_min_points.empty and not y_max_points.empty:
        min_y_point = y_min_points.iloc[0]
        max_y_point = y_max_points.iloc[0]

        second_max_y_points = filtered[
            filtered['y'].isin(filtered['y'].nlargest(2))
            & (filtered['y'] != max_y_point['y'])]
        if not second_max_y_points.empty:
            second_max_y_point = second_max_y_points.iloc[0]
        else:
            second_max_y_point = max_y_point

        if (abs(min_y_point['x'] - max_y_point['x'])
                < abs(min_y_point['x'] - second_max_y_point['x'])):
            endpoint = second_max_y_point
        else:
            endpoint = max_y_point

        if ((filtered['y'].max() - filtered['y'].min())
                > (filtered['x'].max() - filtered['x'].min())):
            obj = Rotate(dataframe)
            return obj.rotate_object(dataframe, endpoint, 90, True)

    return dataframe


def calculate_rad(angle, end_point):
    if angle > 100 and end_point['y'] < 0:
        angle_rad = math.radians(angle + 180)
    elif angle > 100:
        angle_rad = math.radians(-angle)
    elif angle < 45 and end_point['y'] > 0:
        angle_rad = math.radians(-angle)
    elif angle < 45:
        angle_rad = math.radians(angle)
    elif end_point['y'] < 0:
        angle_rad = math.radians(angle)
    else:
        angle_rad = math.radians(-angle)
    return angle_rad


class Rotate:

    def __init__(self, dataframe):
        self.dataframe = dataframe

    @staticmethod
    def rotate_object(data, end_point, angle, corridor):
        if 45 < angle < 135 and corridor or not corridor:
            angle_rad = calculate_rad(angle, end_point)

            cos_angle = math.cos(angle_rad)
            sin_angle = math.sin(angle_rad)

            data['x_rotate'] = data['x'] * cos_angle - data['y'] * sin_angle
            data['y_rotate'] = data['x'] * sin_angle + data['y'] * cos_angle

            data = data.drop(columns=['y', 'x'])
            data = data.rename(columns={'x_rotate': 'x'})
            data = data.rename(columns={'y_rotate': 'y'})
            return data
        else:
            return data

    def turn_room(self, gang):
        data = self.dataframe
        finish = False
        if not gang:
            data = data.rename(columns={'y': 'z_orig'})
            data = data.rename(columns={'z': 'y'})

        """
        Rotate the room data so that the line from the last
        point to the 'Start' point is parallel to the X axis.
        """
        start_points = data[data['type'] == 'Start']
        end_point = data.iloc[-1]
        if len(start_points) > 1:
            if not gang:
                gang = True
                # We pick a random door and see that it works with that one
                try:
                    unique_values = data['room'].unique()
                    filtered_values = [value for value in unique_values if
                                       value not in
                                       ['start', 'default', 'corner']]
                    random_value = np.random.choice(filtered_values)
                    random_pair = data[data['room'] == random_value]
                    if len(random_pair) == 2:
                        start_points = random_pair[
                            random_pair['type'] == 'Start'].iloc[0]
                        end_point = random_pair[
                            random_pair['type'] != 'Start'].iloc[0]
                    else:
                        print(f"turn error: Not enough points")
                        start_points = start_points.iloc[0]
                except Exception as e:
                    print(f"turn error: {e}")
                    start_points = start_points.iloc[0]
                    room = start_points['room']
                    end_point = data[data['room'] == room
                                     & data[data['type'] == 'door']].iloc[0]

            else:
                gang = False
                finish = True
                points = get_nodes(data)
                start_points = points[0]
                end_point = points[1].iloc[0]
        else:
            start_points = start_points.iloc[0]

        data['x'] -= start_points['x']
        data['y'] -= start_points['y']
        end_point = end_point.copy()
        end_point['x'] -= start_points['x']
        end_point['y'] -= start_points['y']
        if type(end_point['x']) is not (float and np.float64):
            angle = calculate_angle_dot_product(
                end_point['x'].iloc[0], end_point['y'].iloc[0])
        else:
            angle = calculate_angle_dot_product(end_point['x'], end_point['y'])
        data = self.rotate_object(data, end_point, angle, False)
        if not gang or gang is None:
            if finish:
                data = validate_rotation(data)
            return data
        else:
            self.dataframe = data
            return self.turn_room(True)
