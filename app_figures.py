import pandas as pd
import plotly.express as px


class Data:
    """
    Load Data and generate DataFrames
    """

    def __init__(self) -> None:
        # Get deplacements for 2021 with start_time as index and converted to time object
        self.data_stations_2021 = pd.read_csv("data\\2021_donnees_ouvertes.csv")
        self.data_stations_2021["start_date"] = pd.to_datetime(
            self.data_stations_2021["start_date"]
        )
        self.data_stations_2021.set_index("start_date", inplace=True)

        # Get Bixi station loc (used for jointure and to get location of stations)
        self.bixi_stations = pd.read_csv("data\\2021_stations.csv")

        # To avoid because we will choose a period (here is for the sum of the year):
        # Get station Bixi count
        self.count_stations = pd.read_csv("data\\2021_count_stations.csv")
        # Get all number of deplacements
        self.deplacements_trajets = pd.read_csv("data\\deplacement.csv")

    def get_deplacements_count(self,filtered_df: pd.DataFrame):
        """
        Returns a dataframe with the id and name of the station, the latitude and longitude and the number of trajets
        """
        # Get the number of trajets
        count_stations=filtered_df["emplacement_pk_start"].value_counts()
        count_stations=pd.DataFrame({"station_id":count_stations.index,"nb_trajets":count_stations.values}).set_index("station")
        
        # Join the station_id with the name and the coordinates
        count_stations=count_stations.merge(self.bixi_stations,left_on="station_id",right_on="pk")
        count_stations=count_stations[["pk","name","latitude","longitude","nb_trajets"]]
        count_stations.set_index("name",inplace=True)
        return count_stations     

    @classmethod
    def filter_by_date(cls, df: pd.DataFrame, begin_date: str, end_date: str):
        # deplacement_with_time.loc["2021-01-10":"2021-06-10"]
        return df.loc[begin_date:end_date]

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
            zoom=9.25,
            center={"lat": 45.5569442, "lon": -73.6336101},
        )
        # If bixi_stations
        # fig = px.scatter_mapbox(
        #     stations,
        #     lat="latitude",
        #     lon="longitude",
        #     hover_name="name",
        #     zoom=9.25,
        #     center={"lat": 45.5569442, "lon": -73.6336101},
        # )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return fig
