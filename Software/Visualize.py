# Copyright (c) Noah Meißner.
# Licensed under the MIT License.


import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random


class Visualize:

    def __init__(self, dataframe):
        self.dataframe = dataframe

    def show_raw_plan(self):
        fig = make_subplots(rows=1, cols=1)

        dataframe = self.dataframe
        for point_type, color in [('Start', 'blue'), ('door', 'green'), ('corner', 'red'),
                                  ('elevator', 'yellow'), ('Init', 'black')]:
            points = dataframe[dataframe['type'] == point_type]

            fig.add_trace(go.Scatter(
                x=points['x'],
                y=points['y'],
                text=points.index.astype(str),
                mode='markers+text',
                marker=dict(color=color, size=8),
                textposition='top center',
                name=point_type
            ))

        for room in dataframe['room'].unique():
            room_points = dataframe[(dataframe['room'] == room) & (dataframe['orig'] == 'room')].sort_index()
            if len(room_points) > 1:
                fig.add_trace(go.Scatter(
                    x=room_points['x'],
                    y=room_points['y'],
                    mode='lines',
                    line=dict(color='black', width=2),
                    showlegend=False
                ))

        for corridor in dataframe['corridor'].unique():
            corridor_points = dataframe[
                (dataframe['corridor'] == corridor) & (dataframe['orig'] == 'init')].sort_index()
            if len(corridor_points) > 1:
                fig.add_trace(go.Scatter(
                    x=corridor_points['x'],
                    y=corridor_points['y'],
                    mode='lines',
                    line=dict(color='orange', width=2),
                    showlegend=False
                ))

        fig.update_layout(
            title='Ground Visualization',
            xaxis_title='X in Meters',
            yaxis_title='Y in Meters'
        )
        fig.show()

    def show_multiple_rooms(self):
        ls = ['BA526', 'BA528', 'BA529', 'BA530', 'BA531', 'BA532', 'BA533', 'BA534', 'BA535', 'BA527']
        colors = {}
        for room in ls:
            colors[room] = f'#{random.randint(0, 0xFFFFFF):06x}'

        data = self.dataframe
        dataframe = pd.DataFrame()
        for room in data:
            name = room['room'].iloc[0]
            if name in ls:
                room_start = room[room['type'] == 'Start'].iloc[0]
                room_y_max = max(room[room['type'] == 'corner']['y'])

                room_end_door = room.tail(1)
                vector_x = room_start['x'] - room_end_door['x'].values[0]
                vector_y = room_start['y'] - room_y_max

                if abs(vector_y) > 1:
                    room['y'] = -room['y']
                if vector_x < 0:
                    room['x'] = -room['x']
                if dataframe.empty:

                    dataframe = room
                else:
                    dataframe = pd.concat([dataframe, room])

        fig = make_subplots(rows=1, cols=1)

        for point_type, color in [('Start', 'blue'), ('door', 'green'), ('corner', 'red'),
                                  ('elevator', 'yellow'), ('Init', 'black')]:
            points = dataframe[dataframe['type'] == point_type]

            fig.add_trace(go.Scatter(
                x=points['x'],
                y=points['y'],
                mode='markers+text',
                marker=dict(color=color, size=8),
                textposition='top center',
                name=point_type
            ))

        for room in dataframe['room'].unique():
            room_points = dataframe[(dataframe['room'] == room)].sort_index()
            if len(room_points) > 1:
                room_color = colors[room]
                fig.add_trace(go.Scatter(
                    x=room_points['x'],
                    y=room_points['y'],
                    mode='lines',
                    line=dict(color=room_color, width=2),
                    showlegend=False
                ))

        fig.show()
