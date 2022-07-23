import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import matplotlib as mpl

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


class Data:
    """
    Load Data and generate DataFrames
    """

    def __init__(self) -> None:
        print("Loading data...")
        start_time = time.perf_counter()

        self.get_open_data()
        self.get_deplacements_per_month_per_station()

        # self.data_stations_2021 = self.data_stations_2021.merge(
        #     self.bixi_stations, left_on="emplacement_pk_start", right_on="pk"
        # ).drop(columns=["pk"])

        # To avoid because we will choose a period (here is for the sum of the year):
        # Get station Bixi count
        # self.count_stations = pd.read_csv("data/2021_count_stations.csv")
        
        # Get all number of deplacements
        self.deplacements = pd.read_csv("data/2021_deplacements.csv")
        
        end_time = time.perf_counter()
        print(f"Data loaded! Time needed: {end_time-start_time:.1f} s")

    def get_open_data(self):
        # Get deplacements for 2021 (for now) with start_time as index and converted to time object
        # TODO: get displacement for all years
        self.data_stations_2021 = pd.read_csv("data/2021_donnees_ouvertes.csv")
        self.data_stations_2021["start_date"] = pd.to_datetime(
            self.data_stations_2021["start_date"]
        )

        # The following is usefull for the timeline
        self.data_stations_2021.sort_values(by="start_date", inplace=True)
        self.data_stations_2021["Day"] = self.data_stations_2021[
            "start_date"
        ].dt.day_name()

        self.data_stations_2021["Month"] = self.data_stations_2021[
            "start_date"
        ].dt.month

        self.min_month_idx = self.data_stations_2021["Month"].min()
        self.max_month_idx = self.data_stations_2021["Month"].max()

        # Get Bixi station loc (used for merge and to get location of stations)
        self.bixi_stations = pd.read_csv("data/2021_stations.csv")

    def get_deplacements_per_month_per_station(self):
        # Create dict of deplacement over month for each station
        # pk=10 : month=[4,5...] nb_trajets=[29238,29323,...]
        df_pk_group = self.data_stations_2021.groupby("emplacement_pk_start")
        self.nb_trajets_dict = {}
        for pk, df in df_pk_group:
            df = df.groupby("Month").count().filter(items=["start_date"])
            df = df.rename({"start_date": "nb_trajets"})
            self.nb_trajets_dict[pk] = df

    def get_deplacements_count(self, filtered_df: pd.DataFrame):
        """
        Returns a dataframe with the id and name of the station, the latitude and longitude and the number of trajets
        """
        # Get the number of trajets
        count_stations = filtered_df["emplacement_pk_start"].value_counts()
        count_stations = pd.DataFrame(
            {"station_id": count_stations.index, "nb_trajets": count_stations.values}
        ).set_index("station_id")

        # Join the station_id with the name and the coordinates
        count_stations = count_stations.merge(
            self.bixi_stations, left_on="station_id", right_on="pk"
        )
        count_stations = count_stations[
            ["pk", "name", "latitude", "longitude", "nb_trajets"]
        ]
        # count_stations.set_index("name",inplace=True)
        return count_stations

    def get_stations_deplacement(self, station_name_list):
        """
        get in the deplacement_by_months dict the dataframes that correspond
        and return it
        """
        station_list_id = [
            self.bixi_stations.loc[self.bixi_stations["name"] == name]["pk"].values[0]
            for name in station_name_list
        ]
        nb_trajets_dict_name = {
            station_name: self.nb_trajets_dict[station_list_id[idx]]
            for idx, station_name in enumerate(station_name_list)
        }
        return nb_trajets_dict_name


class Figures:
    """
    Create Figures for Dash App
    """

    def __init__(self) -> None:
        pass

    def create_stations_map(self, stations: pd.DataFrame):
        # If deplacement_sum
        fig = px.scatter_mapbox(
            stations,
            lat="latitude",
            lon="longitude",
            hover_name="name",
            size="nb_trajets",
            color="nb_trajets",
            custom_data=["pk"],
            zoom=9.25,
            center={"lat": 45.5569442, "lon": -73.6336101},
        )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        fig.update_layout(clickmode="event+select")
        return fig

    def create_stations_deplacement_history(self, dfs_dict):
        fig = go.Figure()
        for station_name, df in dfs_dict.items():
            fig.add_trace(go.Scatter(x=df.index, y=df["start_date"], name=station_name))
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
        )
        return fig
    
    def create_stations_deplacement_map(self,deplacements:pd.DataFrame, pickup_name:str):
        # Color bounds for the value gradient
        c1="#22c1c3"
        c2="#fdbb2d"
        
        df=deplacements

        # Width line bounds according to value
        min_max_width = [1, 4]
        min_max_nb = [
            df[df["pickup_name"] == pickup_name]["nb"].min(),
            df[df["pickup_name"] == pickup_name]["nb"].max(),
        ]

        fig = go.Figure()
        for idx in df[df["pickup_name"] == pickup_name].index:
            fig.add_trace(
                go.Scattermapbox(
                    mode="lines",
                    # name="to ...",
                    lat=[df["pickup_latitude"][idx], df["dropoff_latitude"][idx]],
                    lon=[df["pickup_longitude"][idx], df["dropoff_longitude"][idx]],
                    line=dict(
                        color=Figures._color_fader(c1,c2,np.interp(df["nb"][idx],min_max_nb,[0,1])),
                        width=np.interp(df["nb"][idx], min_max_nb, min_max_width),
                    ),
                )
            )

        fig.update_layout(
            margin={"l": 0, "t": 0, "b": 0, "r": 0},
            mapbox={
                "style": "open-street-map",
                "center": {"lat": 45.5569442, "lon": -73.6336101},
                "zoom": 9.25,
            },
            showlegend=False,
        )
        return fig
        
    @classmethod
    def _color_fader(cls,c1,c2,mix=0): #fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
            c1=np.array(mpl.colors.to_rgb(c1))
            c2=np.array(mpl.colors.to_rgb(c2))
            return mpl.colors.to_hex((1-mix)*c1 + mix*c2)


if __name__ == "__main__":
    data = Data()
    print(data.data_stations_2021)
