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

app.layout = html.Div([
    html.Div([
        html.H6('Code Chef Level 1')],
        style={'margin': '20px', 'width': '220px'}
    ),

    dbc.Row([
        html.Div(
            [
                dcc.Upload(
                    id='files-upload', 
                    children=html.Button('Select TAB, WAX & Dataset Files'),
                    multiple=True
                )
            ],
            style={'padding': '0px 0px 0px 50px'},
        ),

        html.Div([
            dbc.Button('Open user defined inputs', id='User-defined-inputs'),
            dbc.Modal([
                dbc.ModalHeader(
                    'Parameters :',
                    style={'margin': '20px', 'width': '130px', 'padding': '10px 5px'}
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
                        'Re-calculate', id='close-popup', className='ml-auto',
                        style={'margin': '20px', 'width': '170px'}
                    )
                )
            ], 
            id='modal')],
            style={'padding': '0px 0px 0px 50px'}
        ),

        html.Div([
            dbc.Button('Open printout', id='printout-output'),
            dbc.Modal([
                dbc.ModalHeader(
                    'Calculation printout :',
                    style={'margin': '20px', 'width': '260px', 'padding': '10px 5px'}
                ),
                dbc.ModalBody(html.Div(id='text-display')),
                dbc.ModalFooter(
                    dbc.Button(
                        'Close', id='close-popup-printout', className='ml-auto',
                        style={'margin': '20px', 'width': '170px'}
                    )
                )
            ], 
            id='modal-printout',size='lg')],
            style={'padding': '0px 0px 0px 50px'}
        ),

        html.Div([
            dcc.Checklist(
                id='printout-checklist',
                options=[
                    {'label' : 'Keep calculation records', 'value':'track'}
                ],
                value=[], labelStyle={'display': 'inline-block'}
            )],
            style={'padding': '0px 0px 0px 50px'}
        ),
    ]),

    html.Div(
        [
            html.Button(
                id='Rerun' 
            )
        ],
        style={'width': '220px', 'padding': '10px 5px'},
    ),

    html.Div(
        [
            html.Ul('Uploaded files :'),
            html.Ul(id='file-list')
        ],
        style={'margin': '20px', 'display': 'inline-block'}
    ),
    
    dcc.Tabs(id="tabs-styled-with-props", value='tab-1', 
        children=[
            dcc.Tab(label='Inputs / Results', value='tab-1', id='tab-1'),
            dcc.Tab(label='\u03B4', value='tab-2',  id='tab-2'),
            dcc.Tab(label='Fw', value='tab-3', id='tab-3') ,
            dcc.Tab(label='d\u03B4/dt', value='tab-4', id='tab-4') 
        ], 
        colors={
            "border": "white",
            "primary": "gold",
            "background": "cornsilk"
        }
    )

], style={'rowCount':8})

@app.callback(
    Output('modal', 'is_open'),
    [Input('User-defined-inputs', 'n_clicks'), Input('close-popup', 'n_clicks')],
    [State('modal', 'is_open')]
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
    [
        Output('file-list', 'children'),
        Output('tab-1', 'children'),
        Output('tab-2', 'children'),
        Output('tab-3', 'children'),
        Output('tab-4', 'children'),
        Output('text-display', 'children')
    ],
    [
        Input('files-upload', 'filename'),
        Input('files-upload', 'contents'),
        Input('printout-checklist', 'value'),
        Input('close-popup-printout', 'n_clicks')
    ],
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
def tab_outputs(
    filenames, filecontents, trackchecklist, n_close,
    C1, C2, C3, DI, MO, PIO, TOI, DowMethod
):

    if filenames is not None and filecontents is not None:
        for name, data in zip(filenames, filecontents):
            CCA.save_file(name, data)

    files = CCA.uploaded_files()

    final_text = '''
                \n\t No printout file available yet. 
                \n\t Please tick "Keep calculation record" to start recording.
                '''

    if len(files)==0:
        file_list = [html.Li('No files yet! Please use "Select TAB, WAX, Dataset Files"')]
        children1, children2, children3, children4 = [[html.Li('Not enough input files')]]*4
    else:
        file_list = [html.Li(file) for file in files]
        if len(files)==3:
            datafiles = {
                ftype:'./temp/'+f 
                for ftype in ['tab','wax','xlsx'] 
                for f in files 
                if f.endswith(ftype)
            }

            track = True if trackchecklist else False
            
            L1 = Master(
                datafiles, 
                float(C1), 
                float(C2), 
                float(C3), 
                float(DI), 
                float(MO), 
                float(PIO), 
                float(TOI), 
                DowMethod, 
                track
            )

            dfIO = L1.dfOutputs

            fig1 = CCA.generate_plot(dfIO,'\u03B4 (mm)')
            fig2 = CCA.generate_plot(dfIO,'Fw (Frac.)')
            fig3 = CCA.generate_plot(dfIO,'d\u03B4/dt (mm/s)')

            children1 = [CCA.generate_table(dfIO)]
            children2 = [dcc.Graph(figure=fig1)]
            children3 = [dcc.Graph(figure=fig2)]
            children4 = [dcc.Graph(figure=fig3)]

            if trackchecklist:
                text_markdown = '\t'
                if os.path.isfile('./printout.txt'):
                    with open('./printout.txt') as handle:
                        for line in handle.read():
                            text_markdown += line
                final_text = '''{}'''.format(text_markdown)
            
        else:
            children1, children2, children3, children4 = [[html.Li('Not enough input files')]]*4

    return file_list, children1, children2, children3, children4, dcc.Markdown(final_text)

if __name__ == '__main__':
    # hostname = socket.gethostname()
    # hostIP = socket.gethostbyname(hostname)
    # app.server.run(port=8080, host=hostIP)
    app.run_server(debug=True)