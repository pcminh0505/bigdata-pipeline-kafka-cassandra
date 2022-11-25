# import pandas
import pandas as pd
import os
import pathlib
import numpy as np
import datetime as dt
import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from scipy.stats import rayleigh
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import iplot
from plotly.subplots import make_subplots

from cassandrautils import *

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Dash"

server = app.server

app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

app.layout = html.Div(
    [
        # header
        html.Div(
            [
                html.Div(
                    [
                        html.H4("Visualization with Dash", className="app__header__title"),
                        html.P(
                            "This app continually queries Cassandra database and displays live charts based on the current data.",
                            className="app__header__title--grey",
                        ),
                    ],
                    className="app__header__desc",
                ),
                
            ],
            className="app__header",
        ),
        html.Div(
            [
                # weather
                html.Div(
                    [
                        html.Div([
                            html.H5("Temperature line chart (OWM data)"),
                            dcc.Dropdown(
                                id='checklist', 
                                value='temp', 
                                options=[{'value': x, 'label': x} 
                                        for x in ['temp', 'temp_max', 'temp_min', 'feels_like', 'wind']],
                                clearable=False
                            ),
                            dcc.Graph(id="line-chart"),
                        ])
                    ],
                    className="one-half column",
                ),
                # faker
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div([
                                    html.H5("Histogram of age (Faker data)"),
                                    html.P("Number of bin:"),
                                    dcc.Slider(id="num_bin", min=5, max=10, step=1, value=6),
                                    dcc.Graph(id="graph"),
                                ])
                            ],
                            className="graph__container first",
                        ),
                    ],
                    className="one-half column",
                ),
            ],
            className="app__content",
        ),
        html.Div(
            [
                html.Div([
                    html.H5("Crypto Market Stream - 1m Interval"),
                    dcc.Dropdown(
                        id='checklist-crypto', 
                        value='BTCUSDT', 
                        options=[{'value': x, 'label': x} 
                                    for x in ['BTCUSDT', 'ETHUSDT']],
                        clearable=False
                    ),
                    dcc.Graph(id="graph-crypto"),
                ])
            ],
            className="app__content",
        ),
    ],
    className="app__container",
)

@app.callback(
    Output("line-chart", "figure"), 
    [Input("checklist", "value")])
def update_line_chart(col):
    df = getWeatherDF()
    df['forecast_timestamp'] = pd.to_datetime(df['forecastdate'])
    # Convert Kelvin to Celsius
    df[['feels_like','temp','temp_max','temp_min']] = df[['feels_like','temp','temp_max','temp_min']].transform(lambda x: x - 273.15)
    fig = px.line(df, 
        x="forecast_timestamp", y=col, color='location')
    return fig


@app.callback(
    Output("graph", "figure"), 
    [Input("num_bin", "value")])
def display_color(num_bin):
    df = getFakerDF()
    currentYear = dt.date.today().year
    df['age'] = df['year'].apply(lambda x: int(currentYear-x))
    fig = px.histogram(df['age'], nbins=num_bin, range_x=[0, 100])
    return fig

@app.callback(
    Output("graph-crypto", "figure"), 
    [Input("checklist-crypto", "value")])
def display_candlestick(pair):
    df = getBinanceDF()
    df = df[(df.pair == pair)]

    # Calculate bollinger bands
    WINDOW = 99
    df['sma'] = df['close_price'].rolling(WINDOW, min_periods=1).mean()
    df['std'] = df['close_price'].rolling(WINDOW, min_periods=1).std()

    # Create subplots with 2 rows; top for candlestick price, and bottom for bar volume
    fig = make_subplots(rows = 2, cols = 1, 
                        shared_xaxes = True,
                        subplot_titles = (pair, 'Volume'))

    # ----------------
    # Candlestick Plot
    fig.add_trace(go.Candlestick(x = df['datetime'],
                                open = df['open_price'],
                                high = df['high_price'],
                                low = df['low_price'],
                                close = df['close_price'], showlegend=False,
                                name = 'Candlestick'),
                                row = 1, col = 1)

    # Define the parameters for the Bollinger Band calculation
    ma_size = 20
    bol_size = 2

    # Calculate the SMA
    df.insert(0, 'moving_average', df['close_price'].rolling(ma_size).mean())

    # Calculate the upper and lower Bollinger Bands
    df.insert(0, 'bol_upper', df['moving_average'] + df['close_price'].rolling(ma_size).std() * bol_size)
    df.insert(0, 'bol_lower', df['moving_average'] - df['close_price'].rolling(ma_size).std() * bol_size)

    # Remove the NaNs -> consequence of using a non-centered moving average
    df.dropna(inplace=True)

    # Plot the three lines of the Bollinger Bands indicator -> With short amount of time, this can look ugly
    # for parameter in ['moving_average', 'bol_lower', 'bol_upper']:
    #     fig.add_trace(go.Scatter(
    #         x = df['datetime'],
    #         y = df[parameter],
    #         showlegend = False,
    #         line_color = 'gray',
    #         mode='lines',
    #         line={'dash': 'dash'},
    #         marker_line_width=2, 
    #         marker_size=10,
    #         opacity = 0.8))

    # Volume Plot
    fig.add_trace(go.Bar(x = df['datetime'], y = df['volume'], showlegend=False), 
                row = 2, col = 1)

    # Remove range slider; (short time frame)
    fig.update(layout_xaxis_rangeslider_visible=False)
    return fig

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True, dev_tools_ui=True)


