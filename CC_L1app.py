import os
import socket
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import CC_AppModules as cca

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
buttonstyle = {'padding': '0px 0px 0px 20px','display':'inline-block'}

app.layout = html.Div([
    html.Div([
        html.Content(html.B('Code Chef Level 1'))],
        style={
            'padding': '20px 0px 5px 20px',
            'background-color':'bisque',
            'font-size':'30px', 
            'text-align': 'center',
            'color': 'darkslategray'
        }
    ),

    html.Div(
        [
            html.Div(
                dcc.Upload(
                    id='files-upload', 
                    children=dbc.Button(
                        'Select TAB, WAX & Dataset Files',
                        style={'background-color':'darkslategray'}
                    ),
                    multiple=True
                ),
                style=buttonstyle
            ),

            html.Div([
                dbc.Button('Uploaded file list', 
                    id='open-file-list', 
                    style={'background-color':'darkslategray'}
                ),
                dbc.Modal([
                    dbc.ModalHeader('Uploaded files :'),
                    dbc.ModalBody(html.Div(
                        id='body-file-list',
                        style={'padding': '20px 0px 5px 20px'}
                    )),
                    dbc.ModalFooter(
                        dbc.Button('Close', 
                            id='close-file-list', className='ml-auto'
                        )
                    )
                ], 
                id='modal-file-list',size='lg')],
                style=buttonstyle
            ),

            html.Div([
                dbc.Button('Open user defined inputs', 
                    id='open-user-inputs',
                    style={'background-color':'darkslategray'}
                ),
                dbc.Modal([
                    dbc.ModalHeader(
                        'Parameters :'
                    ),
                    cca.input_parameters(0),
                    cca.input_parameters(1),
                    cca.input_parameters(2),
                    cca.input_parameters(3),
                    cca.input_parameters(4),
                    cca.input_parameters(5),
                    cca.input_parameters(6),
                    cca.input_parameters(7),
                    dbc.ModalFooter(
                        dbc.Button(
                            'Close', id='close-user-inputs', className='ml-auto'
                        )
                    )
                ], 
                id='modal-inputs')],
                style=buttonstyle
            ),

            html.Div(
                html.Button('Run',
                    id='run-button',
                    style={'background-color':'burlywood'}
                ),
                style=buttonstyle,
            ),
        ],
        style={
            'padding': '20px 0px 20px 0px',
            'background-color':'blanchedalmond',
            'text-align': 'center',
        }
    ),

    html.Div(
        [
            dcc.Tabs(id='tabs', value='tab-1', 
                colors={
                    "border":'white',
                    "primary": 'bisque',
                    "background": 'cornsilk'
                },
                style={'align-items': 'center'}
            )
        ],
        style={
            'padding': '20px 20px 5px 20px',
            'font-size':'15px', 
            'text-align': 'center',
            'font-family': 'Cambria',
            'color': 'darkslategray'
        }
    ),

])

cca.file_upload(app, 'files-upload', 'body-file-list')
cca.open_modal(app, 'modal-file-list', 'open-file-list', 'close-file-list')
cca.open_modal(app, 'modal-inputs', 'open-user-inputs', 'close-user-inputs')
cca.tabs_display(app)

if __name__ == '__main__':
    hostname = socket.gethostname()
    hostIP = socket.gethostbyname(hostname)
    app.server.run(port=8080, host=hostIP)
    # app.run_server(debug=True)