import os
import flask
import webbrowser
import socket
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input
import plotly.express as px
import CC_AppModules_L2 as cca

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
buttonstyle = {'padding': '0px 0px 0px 20px','display':'inline-block'}

app.layout = html.Div([
    html.Div([
        html.Content(html.B('Team Citral Code Chef Level 2'))],
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
            html.Div([
                dbc.Button('Algorithm Info', 
                    id='open-info', 
                    style={'background-color':'darkslategray'}
                ),
                dbc.Modal([
                    dbc.ModalHeader('Level 2 Algorithm'),
                    dbc.ModalBody(
                        html.Img(
                            src=app.get_asset_url('algorithm_2.PNG')
                        )
                    ),
                    dbc.ModalFooter(
                        dbc.Button('Close', 
                            id='close-info', className='ml-auto'
                        )
                    )
                ], 
                id='modal-info',size='xl')],
                style=buttonstyle
            ),

            html.Div(
                dcc.Upload(
                    id='files-upload', 
                    children=dbc.Button(
                        'Select TAB & Dataset (Input & Coolant) Files',
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

cca.open_modal(app, 'modal-info', 'open-info', 'close-info')
cca.file_upload(app, 'files-upload', 'body-file-list')
cca.open_modal(app, 'modal-file-list', 'open-file-list', 'close-file-list')
cca.open_modal(app, 'modal-inputs', 'open-user-inputs', 'close-user-inputs')
cca.tabs_display(app)

if __name__ == '__main__':
    hostname = socket.gethostname()
    hostIP, hostport = socket.gethostbyname(hostname), 8080
    webbrowser.open('http://{}:{}'.format(hostIP,hostport))
    app.server.run(port=hostport, host=hostIP)
