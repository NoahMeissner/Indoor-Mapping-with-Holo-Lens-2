# Copyright (c) Noah Meißner.
# Licensed under the MIT License.

"""
Was hier im Skript passiert
"""

from Rotate import Rotate
from LinkRoomCorridor import Graph
from CombineCorridors import Combine
import pandas as pd
import os
from Visualize import Visualize

PATH = ''


def detect_csv_delimiter(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        first_line = file.readline()
        comma_count = first_line.count(',')
        semicolon_count = first_line.count(';')

        if comma_count > semicolon_count:
            return ','
        elif semicolon_count > comma_count:
            return ';'
        else:
            raise ValueError("The separator could not be clearly recognised.")


def rename_german_columns(df):
    df['type'] = df['type'].replace({'Raumecke': 'corner', 'Durchgangstür': 'door', 'Aufzugstür': 'elevator'})
    return df


def process_main():
    ls_frames = []

    for filename in os.listdir(PATH):
        if filename.endswith('.csv'):
            file_path = os.path.join(PATH, filename)
            delimiter = detect_csv_delimiter(file_path)
            df = pd.read_csv(file_path, sep=delimiter)
            renamed_df = rename_german_columns(df)
            turn_element = Rotate(renamed_df)
            ls_frames.append(turn_element.turn_room(False))
    # Link Rooms with floor
    make_graph = Graph(ls_frames)
    dataframe = make_graph.get_plan()
    # Add Floors together
    combine_object = Combine(dataframe)
    dataframes = combine_object.combine()
    # Visualize Entire Floor
    v = Visualize(dataframes)
    v.show_raw_plan()


process_main()
