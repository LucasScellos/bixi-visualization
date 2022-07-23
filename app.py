from itertools import count
import json
from dash import Dash, html, dcc, Input, Output, ctx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app_figures import Data, Figures, MONTHS

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]


class DashApp:
    def __init__(self) -> None:
        # Import Bixi Data
        self.data = Data()

        # Create figures
        self.fig_creator = Figures()

        self.app = Dash(__name__)

        self.app.layout = html.Div(
            [
                html.Div([html.H1("Bixi Visualisation")], className="banner"),
                html.Div(
                    [
                        html.H3("Bixi Map - Deplacement Analysis in year 2021"),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P("Month Timeline for 2021"),
                                        dcc.RangeSlider(
                                            min=self.data.min_month_idx,
                                            max=self.data.max_month_idx,
                                            step=1,
                                            value=[
                                                self.data.min_month_idx,
                                                self.data.max_month_idx,
                                            ],
                                            marks={
                                                idx + 1: MONTHS[idx]
                                                for idx in range(
                                                    self.data.min_month_idx - 1,
                                                    self.data.max_month_idx,
                                                )
                                            },
                                            id="stations_map_slider_timeline",
                                        ),
                                    ],
                                    id="div_slider_timeline",
                                    className="six columns",
                                ),
                                html.Div(
                                    [
                                        html.P("How many best stations would you see?"),
                                        dcc.Slider(
                                            min=1,
                                            max=len(self.data.bixi_stations),
                                            step=None,
                                            value=len(self.data.bixi_stations),
                                            id="stations_map_slider_best",
                                        ),
                                    ],
                                    id="div_slider_best_bixis",
                                    className="six columns",
                                ),
                            ],
                            className="row",
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Graph(id="stations_map"),
                            ],
                            # className="seven columns",
                        ),
                        html.Div(
                            [
                                html.H5(
                                    "Click or select stations on the map to show deplacement over year"
                                ),
                                dcc.Graph(id="station_deplacement_figure"),
                            ],
                            # className="five columns",
                        ),
                    ],
                    # className="row",
                ),
                html.Div(
                    [
                        html.H5(id="station_deplacement_h5"),
                        dcc.Graph(id="station_deplacement_map"),
                    ]
                ),
                html.P(id="dummy"),
            ]
        )

        # Callback for the station map and the timeline and best sliders
        @self.app.callback(
            Output("stations_map", "figure"),
            Output("stations_map_slider_best", "max"),
            Input("stations_map_slider_timeline", "value"),
            Input("stations_map_slider_best", "value"),
        )
        def update_figure(timeline, best_idxs):
            begin_month = timeline[0]
            end_month = timeline[1]

            filtered_df = self.data.data_stations_2021[
                (self.data.data_stations_2021["Month"] >= begin_month)
                & (self.data.data_stations_2021["Month"] <= end_month)
            ]

            count_df = self.data.get_deplacements_count(filtered_df)
            count_df.sort_values(by="nb_trajets", ascending=False, inplace=True)

            return self.fig_creator.create_stations_map(count_df[:best_idxs]), len(
                count_df
            )

        # Callback to update station deplacement figure when selected/clicked station on map
        @self.app.callback(
            Output("station_deplacement_figure", "figure"),
            Input("stations_map", "selectedData"),
        )
        def update_station_deplacement_by_months(selectedData):
            if selectedData is None:
                return go.Figure()
            print(selectedData)
            stations_lon_lat = [[pt["lon"], pt["lat"]] for pt in selectedData["points"]]
            stations_names = [pt["hovertext"] for pt in selectedData["points"]]
            # If custom_data=["pk"] is specified for figure:
            stations_id = [pt["customdata"][0] for pt in selectedData["points"]]
            dfs_dict = self.data.get_stations_deplacement(stations_names)
            # print(dfs_dict)
            fig = self.fig_creator.create_stations_deplacement_history(dfs_dict)
            return fig
        
        # # Callback to update station deplacement map when clicked station on map
        # # TODO: Optimize because its lagging a lot...
        # @self.app.callback(
        #     Output("station_deplacement_map", "figure"),
        #     Output("station_deplacement_h5","children"),
        #     Input("stations_map", "clickData"),
        # )
        # def update_station_deplacement_by_months(clickData):
        #     if clickData is None:
        #         return go.Figure(), "No station clicked"
        #     print(clickData)
        #     station_name = clickData["points"][0]["hovertext"]
        #     h5_text=f"Clicked station: {station_name}"
        #     fig = self.fig_creator.create_stations_deplacement_map(self.data.deplacements,station_name)
        #     return fig, h5_text
        
        


if __name__ == "__main__":
    app = DashApp()
    app.app.run_server(debug=True)
