import pandas as pd
import plotly.express as px


class Data:
    """
    Load Data and generate DataFrames
    """

    def __init__(self) -> None:
        self.bixi_stations = pd.read_csv("data\\2021_stations.csv")
        self.depacements_sum = pd.read_csv("data\\deplacement.csv")


class Figures:
    """
    Create Figures for Dash App
    """

    def __init__(self) -> None:
        pass

    def create_stations_map(self, stations: pd.DataFrame):
        fig = px.scatter_mapbox(
            stations,
            lat="latitude",
            lon="longitude",
            hover_name="name",
            zoom=9.25,
            center={"lat": 45.5569442, "lon": -73.6336101},
        )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return fig
