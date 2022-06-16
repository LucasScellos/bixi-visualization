from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px
from app_figures import Data, Figures

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]


class DashApp:
    def __init__(self) -> None:
        # app = Dash(__name__, external_stylesheets=external_stylesheets)
        self.app = Dash(__name__)

        # Import Bixi Data
        self.data = Data()

        # Create figures
        self.fig_creator = Figures()

        self.app.layout = html.Div(
            [
                html.H1("Bixi Data Visualisation"),
                dcc.Graph(id="stations_map"),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P("Month Timeline for 2021"),
                                dcc.RangeSlider(
                                    min=1,
                                    max=12,
                                    step=None,
                                    value=[1, 12],
                                    marks={
                                        str(month): str(month) for month in range(1, 13)
                                    },
                                    id="stations_map_slider_timeline",
                                ),
                            ],
                            id="div_slider_timeline",
                        ),
                        html.P("How many best stations would you see?"),
                        dcc.Slider(
                            min=1,
                            max=len(self.data.count_stations),
                            step=None,
                            value=len(self.data.count_stations),
                            id="stations_map_slider_best",
                        ),
                    ],
                    id="div_slider_best_bixis",
                ),
            ]
        )

        @self.app.callback(
            Output("stations_map", "figure"),
            # Input("stations_map_slider_best", "value"),
            Input("stations_map_slider_timeline", "value"),
        )
        def update_figure(timeline):
            filtered_df = Data.filter_by_date(
                self.data.data_stations_2021,
                f"2021-{timeline[0]}",
                f"2021-{timeline[1]}",
            )
            count_df = self.data.get_deplacements_count(filtered_df)
            # TODO : sort count_df and get max size to update slider_best_bixi
            # TODO : Manage empty dataframe for months like Jan-Mar

            return self.fig_creator.create_stations_map(count_df)

        # df = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')

        # app.layout = html.Div([
        #     html.Div([

        #         html.Div([
        #             dcc.Dropdown(
        #                 df['Indicator Name'].unique(),
        #                 'Fertility rate, total (births per woman)',
        #                 id='crossfilter-xaxis-column',
        #             ),
        #             dcc.RadioItems(
        #                 ['Linear', 'Log'],
        #                 'Linear',
        #                 id='crossfilter-xaxis-type',
        #                 labelStyle={'display': 'inline-block', 'marginTop': '5px'}
        #             )
        #         ],
        #         style={'width': '49%', 'display': 'inline-block'}),

        #         html.Div([
        #             dcc.Dropdown(
        #                 df['Indicator Name'].unique(),
        #                 'Life expectancy at birth, total (years)',
        #                 id='crossfilter-yaxis-column'
        #             ),
        #             dcc.RadioItems(
        #                 ['Linear', 'Log'],
        #                 'Linear',
        #                 id='crossfilter-yaxis-type',
        #                 labelStyle={'display': 'inline-block', 'marginTop': '5px'}
        #             )
        #         ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
        #     ], style={
        #         'padding': '10px 5px'
        #     }),

        #     html.Div([
        #         dcc.Graph(
        #             id='crossfilter-indicator-scatter',
        #             hoverData={'points': [{'customdata': 'Japan'}]}
        #         )
        #     ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
        #     html.Div([
        #         dcc.Graph(id='x-time-series'),
        #         dcc.Graph(id='y-time-series'),
        #     ], style={'display': 'inline-block', 'width': '49%'}),

        #     html.Div(dcc.Slider(
        #         df['Year'].min(),
        #         df['Year'].max(),
        #         step=None,
        #         id='crossfilter-year--slider',
        #         value=df['Year'].max(),
        #         marks={str(year): str(year) for year in df['Year'].unique()}
        #     ), style={'width': '49%', 'padding': '0px 20px 20px 20px'})
        # ])

        # @app.callback(
        #     Output('crossfilter-indicator-scatter', 'figure'),
        #     Input('crossfilter-xaxis-column', 'value'),
        #     Input('crossfilter-yaxis-column', 'value'),
        #     Input('crossfilter-xaxis-type', 'value'),
        #     Input('crossfilter-yaxis-type', 'value'),
        #     Input('crossfilter-year--slider', 'value'))
        # def update_graph(xaxis_column_name, yaxis_column_name,
        #                  xaxis_type, yaxis_type,
        #                  year_value):
        #     dff = df[df['Year'] == year_value]

        #     fig = px.scatter(x=dff[dff['Indicator Name'] == xaxis_column_name]['Value'],
        #             y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
        #             hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name']
        #             )

        #     fig.update_traces(customdata=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'])

        #     fig.update_xaxes(title=xaxis_column_name, type='linear' if xaxis_type == 'Linear' else 'log')

        #     fig.update_yaxes(title=yaxis_column_name, type='linear' if yaxis_type == 'Linear' else 'log')

        #     fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

        #     return fig

        # def create_time_series(dff, axis_type, title):

        #     fig = px.scatter(dff, x='Year', y='Value')

        #     fig.update_traces(mode='lines+markers')

        #     fig.update_xaxes(showgrid=False)

        #     fig.update_yaxes(type='linear' if axis_type == 'Linear' else 'log')

        #     fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
        #                        xref='paper', yref='paper', showarrow=False, align='left',
        #                        text=title)

        #     fig.update_layout(height=225, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})

        #     return fig

        # @app.callback(
        #     Output('x-time-series', 'figure'),
        #     Input('crossfilter-indicator-scatter', 'hoverData'),
        #     Input('crossfilter-xaxis-column', 'value'),
        #     Input('crossfilter-xaxis-type', 'value'))
        # def update_y_timeseries(hoverData, xaxis_column_name, axis_type):
        #     country_name = hoverData['points'][0]['customdata']
        #     dff = df[df['Country Name'] == country_name]
        #     dff = dff[dff['Indicator Name'] == xaxis_column_name]
        #     title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
        #     return create_time_series(dff, axis_type, title)

        # @app.callback(
        #     Output('y-time-series', 'figure'),
        #     Input('crossfilter-indicator-scatter', 'hoverData'),
        #     Input('crossfilter-yaxis-column', 'value'),
        #     Input('crossfilter-yaxis-type', 'value'))
        # def update_x_timeseries(hoverData, yaxis_column_name, axis_type):
        #     dff = df[df['Country Name'] == hoverData['points'][0]['customdata']]
        #     dff = dff[dff['Indicator Name'] == yaxis_column_name]
        #     return create_time_series(dff, axis_type, yaxis_column_name)


if __name__ == "__main__":
    app = DashApp()
    app.app.run_server(debug=True)
