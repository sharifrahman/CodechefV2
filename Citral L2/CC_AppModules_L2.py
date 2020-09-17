import os
import glob
import base64
import pandas as pd
import dash_html_components as html
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from CC_Master_L2 import Master

def generate_table(df):
    return html.Table(
        [
            html.Thead(
                html.Tr([html.Th(col) for col in df.columns])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(df.iloc[i][col]) for col in df.columns
                ]) for i in range(len(df))
            ])
        ],
        style={'margin': '50px',  'font-size': '12px', 'text-align':'center'}
    )

def generate_plot(df, y):

    x_scat, y_scat = df.index.values[1:], df[y].values[1:]

    layout = go.Layout(
        plot_bgcolor="#FFF",
        xaxis=dict(
            title=df.index.name + ' ({})'.format(df.index.values[0]),
            linecolor="#BCCCDC",
            linewidth=2,
            gridcolor="#BCCCDC",
            zeroline = False
        ),
        yaxis=dict(
            title=y + ' ({})'.format(df[y].values[0]),  
            linecolor="#BCCCDC", 
            linewidth=2,
            gridcolor="#BCCCDC",
            zeroline = False,
        ),
        height = 700,
        font = dict(family= 'Cambria', size=15)
    )

    fig = go.Figure(
        data = go.Scatter(x=x_scat, y=y_scat, marker_color='darkslategray', mode='lines+markers'),
        layout = layout
    )
    return fig

def input_parameters(index):

    Parameter = ['Pᵢₒ', 'ɑ']
    Unit = { 
        'Pᵢₒ':'Pa', 
        'ɑ': ''
    }
    DefaultValue = {
        'Pᵢₒ': 101325,
        'ɑ': 'Alpha w'
    }

    Par = Parameter[index]
    if index==0:
        return dbc.ModalBody([
            dbc.ModalBody(
                Par+'\t:',
                style={'width': '50px', 'display': 'inline-block'}
            ),
            dcc.Input(
                id='input-'+str(index), type='text', 
                value = DefaultValue[Par],
                style={'width': '80px', 'display': 'inline-block', 'text-align': 'right'}
            ),
            dbc.ModalBody(
                Unit[Par],
                style={'width': '40px', 'display': 'inline-block'}
            )
        ])
    elif index==1:
        return dbc.ModalBody([
            dbc.ModalBody(
                Par+'\t:',
                style={'width': '50px', 'display': 'block'}
            ),
            dcc.Dropdown(
                id='input-'+str(index),  
                value = DefaultValue[Par],
                options=[
                    {'label': 'ɑw', 'value': 'Alpha w'},
                    {'label': 'ɑc', 'value': 'Alpha c'},
                ],
                style={'width': '80px', 'display': 'block', 'padding': '0px 0px 0px 20px'}
            )
        ])

def file_upload(app, files_upload, body):
    @app.callback(
        Output(body, 'children'),
        [Input(files_upload, 'filename'), Input(files_upload, 'contents')]
    )
    def file_upload(filenames, filecontents):
        if filenames is not None and filecontents is not None:
            for name, content in zip(filenames, filecontents):
                data = content.encode("utf8").split(b";base64,")[1]
                with open(os.path.join('./temp', name), "wb") as fp:
                    fp.write(base64.decodebytes(data))

        files = []
        for filename in os.listdir('./temp'):
            path = os.path.join('./temp', filename)
            if os.path.isfile(path):
                files.append(filename)

        if len(files)==0:
            file_list = [
                html.Content(html.B('No files yet! Please use "Select TAB, WAX, Dataset Files"'))
            ]
        else:
            file_list = [html.Li(html.I(file)) for file in files]
        return file_list

def open_modal(app, modal, button_open, button_close):
    @app.callback(
        Output(modal, 'is_open'),
        [Input(button_open, 'n_clicks'), Input(button_close, 'n_clicks')],
        [State(modal, 'is_open')]
    )
    def toggle_modal(n1,n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

def tabs_display(app):
    @app.callback(
        Output('tabs', 'children'),
        [Input('run-button', 'n_clicks')],
        [
            State('input-0', 'value'),
            State('input-1', 'value')
        ]
    )
    def _(run, PIO, alpha_input):
        children = []
        if run:

            files = []
            for filename in os.listdir('./temp'):
                path = os.path.join('./temp', filename)
                if os.path.isfile(path):
                    files.append(filename)
            datafiles = {
                    ftype:'./temp/'+f 
                    for ftype in ['tab','Inputs.xlsx','Coolant.xlsx'] 
                    for f in files 
                    if f.endswith(ftype)
            }
            if len(datafiles) == 3:
                L2 = Master(
                    datafiles, 
                    alpha_input,
                    float(PIO)
                )
                dfIO = L2.dfOutputs
                if alpha_input=='Alpha w':
                    Variables = ['ɑw','NuD','NuFD','Pro','Reo']
                elif alpha_input=='Alpha c':
                    Variables = ['ɑc','NuD','NuFD','Prc','Rec']

                fig = {
                    var: generate_plot(dfIO, var)
                    for var in Variables
                }

                child = {
                    **{'Results': [generate_table(dfIO)]},
                    **{
                        var: [
                            html.Div(dcc.Graph(figure=fig[var]))
                        ]
                        for var in fig
                    }
                }

                children = [
                    dcc.Tab(child[c], label=c, value='tab-'+str(i+1), id='tab-'+str(i+1))
                    for i, c in enumerate(child)
                ]

        return children
                
