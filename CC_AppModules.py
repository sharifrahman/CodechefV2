import os
import glob
import base64
import pandas as pd
import dash_html_components as html
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from CC_Master import Master

def remove_temp():
    for file in glob.glob('./testfolder'):
        os.remove(file)

def generate_table(df):
    Default_columns = [
        'Time','Tw','dw','δd',
        'Reow','Fo','Fw','Nsr','MVww','π1','π2',
        'Dow','dC/dT','dT/dr','dδ/dt','δ'
    ]
    return html.Table(
        [
            html.Thead(
                html.Tr([html.Th(col) for col in Default_columns])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(df.iloc[i][col]) for col in Default_columns
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
    # if y=='dδ/dt':
    #     fig.write_image('./output/Plot_dδdt.jpg')
    # else:
    #     fig.write_image('./output/Plot_{}.jpg'.format(y))
    return fig

def input_parameters(index):

    Parameter = ['C₁','C₂','C₃', 'dᵢ', 'mₒ', 'Pᵢₒ', 'Tₒᵢ', 'Diffusion rate calculation method']
    Unit = {
        'C₁'    :   '',
        'C₂'    :   '',
        'C₃'    :   '',  
        'dᵢ'    :   'm',  
        'mₒ'    :   'kg/s', 
        'Pᵢₒ'   :   'Pa', 
        'Tₒᵢ'   :   'ᵒC',
        'Diffusion rate calculation method'   :   ''
    }
    DefaultValue = {
        'C₁'    :   15, 
        'C₂'    :   0.055, 
        'C₃'    :   1.4,  
        'dᵢ'    :   0.0446,   
        'mₒ'    :   0.50369,
        'Pᵢₒ'   :   101325,
        'Tₒᵢ'   :   46,
        'Diffusion rate calculation method'   :   'Wilke-Chang'
    }

    Par = Parameter[index]
    if index!=7:
        return dbc.ModalBody([
            dbc.ModalBody(
                Par+'\t:',
                style={'width': '80px', 'display': 'inline-block', 'margin': '5px'}
            ),
            dcc.Input(
                id='input-'+str(index), type='text', 
                value = DefaultValue[Par],
                style={'width': '80px', 'display': 'inline-block', 'margin': '5px', 'text-align': 'right'}
            ),
            dbc.ModalBody(
                Unit[Par],
                style={'width': '80px', 'display': 'inline-block'}
            )
        ])
    else:
        return dbc.ModalBody([
            dbc.ModalBody(
                Par+'\t:',
                style={'width': '170px', 'display': 'inline-block', 'margin': '5px'}
            ),
            dcc.Dropdown(
                id='input-'+str(index),  
                value = DefaultValue[Par],
                options=[
                    {'label': 'Wilke-Chang', 'value': 'Wilke-Chang'},
                    {'label': 'Hayduk-Minhass', 'value': 'Hayduk-Minhass'},
                ],
                style={'width': '160px', 'display': 'inline-block', 'margin': '5px'}
            ),
            dbc.ModalBody(
                Unit[Par],
                style={'width': '80px', 'display': 'inline-block'}
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
            State('input-1', 'value'),
            State('input-2', 'value'),
            State('input-3', 'value'),
            State('input-4', 'value'),
            State('input-5', 'value'),
            State('input-6', 'value'),
            State('input-7', 'value')
        ]
    )
    def toggle_run(run, C1, C2, C3, DI, MO, PIO, TOI, DowMethod):
        children = []
        if run:

            files = []
            for filename in os.listdir('./temp'):
                path = os.path.join('./temp', filename)
                if os.path.isfile(path):
                    files.append(filename)
            datafiles = {
                    ftype:'./temp/'+f 
                    for ftype in ['tab','wax','xlsx'] 
                    for f in files 
                    if f.endswith(ftype)
            }
            if len(datafiles) == 3:
                L1 = Master(
                    datafiles, 
                    float(C1), 
                    float(C2), 
                    float(C3), 
                    float(DI), 
                    float(MO), 
                    float(PIO), 
                    float(TOI), 
                    DowMethod
                )
                dfIO = L1.dfOutputs
                dfIO.to_csv('./output/Output dataframe.csv')
                fig1 = generate_plot(dfIO,'δ')
                fig2 = generate_plot(dfIO,'Fw')
                fig3 = generate_plot(dfIO,'dδ/dt')

                children1 = [generate_table(dfIO)]
                children2 = [html.Div(dcc.Graph(figure=fig1))]
                children3 = [html.Div(dcc.Graph(figure=fig2))]
                children4 = [html.Div(dcc.Graph(figure=fig3))]

                children = [
                dcc.Tab(children1, label='Inputs / Results', value='tab-1', id='tab-1'),
                dcc.Tab(children2, label='δ', value='tab-2',  id='tab-2'),
                dcc.Tab(children3, label='Fw', value='tab-3', id='tab-3') ,
                dcc.Tab(children4, label='dδ/dt', value='tab-4', id='tab-4') 
                ]

        return children
                
