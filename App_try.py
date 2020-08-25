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
import CC_AppModules as CCA
from CC_Master import Master

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
                dbc.Button('Open user defined inputs', 
                    id='User-defined-inputs',
                    style={'background-color':'darkslategray'}
                ),
                dbc.Modal([
                    dbc.ModalHeader(
                        'Parameters :'
                    ),
                    CCA.input_parameters(0),
                    CCA.input_parameters(1),
                    CCA.input_parameters(2),
                    CCA.input_parameters(3),
                    CCA.input_parameters(4),
                    CCA.input_parameters(5),
                    CCA.input_parameters(6),
                    CCA.input_parameters(7),
                    dbc.ModalFooter(
                        dbc.Button(
                            'Close', id='close-popup', className='ml-auto'
                        )
                    )
                ], 
                id='modal-inputs')],
                style=buttonstyle
            ),

            html.Div([
                dbc.Button('Uploaded file list', 
                    id='file-list', disabled=True,
                    style={'background-color':'darkslategray'}
                ),
                dbc.Modal([
                    dbc.ModalHeader('Uploaded file list :'),
                    dbc.ModalBody(html.Div(id='filelist-display')),
                    dbc.ModalFooter(
                        dbc.Button('Close', 
                            id='close-popup-filelist', className='ml-auto'
                        )
                    )
                ], 
                id='modal-filelist',size='lg')],
                style=buttonstyle
            ),

            html.Div([
                dbc.Button('Open printout', 
                    id='printout-output', disabled=True,
                    style={'background-color':'darkslategray'}
                ),
                dbc.Modal([
                    dbc.ModalHeader('Calculation printout :'),
                    dbc.ModalBody(html.Div(id='printout-display')),
                    dbc.ModalFooter(
                        dbc.Button('Close', 
                            id='close-popup-printout', className='ml-auto'
                        )
                    )
                ], 
                id='modal-printout',size='lg')],
                style=buttonstyle
            ),
            html.Div(
                [
                    dcc.Checklist(
                        id='printout-checklist',
                        options=[{'label' : '', 'value':'track'}],
                        value=[], style={'display':'inline-block'},
                    ),
                    html.Content(html.B(' Keep calculations record'),
                        style={'color':'darkslategray'}
                    )
                ],
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

    html.Div([
        html.Content(id='body-text')],
        style={
            'padding': '20px 0px 5px 20px',
            'font-size':'30px', 
            'text-align': 'center'
        }
    ),

])

@app.callback(
    Output('modal-inputs', 'is_open'),
    [Input('User-defined-inputs', 'n_clicks'), Input('close-popup', 'n_clicks')],
    [State('modal-inputs', 'is_open')]
)
def toggle_modal(n1,n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output('modal-printout', 'is_open'),
    [
        Input('printout-output', 'n_clicks'), 
        Input('close-popup-printout', 'n_clicks')
    ],
    [State('modal-printout', 'is_open')]
)
def toggle_modal2(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output('body-text', 'children'),
    [Input('run-button', 'n_clicks')],
)
def toggle_run(n_clicks):
    if n_clicks:
        return 'is_open'

if __name__ == '__main__':
    app.run_server(debug=True)