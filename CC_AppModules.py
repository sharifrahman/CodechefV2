import os
import glob
import base64
import dash_html_components as html
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_bootstrap_components as dbc

def remove_temp():
    for file in glob.glob('./testfolder'):
        os.remove(file)

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
        style={'margin': '50px'}
    )

def generate_plot(df, y):

    x_scat, y_scat = df.index.values[1:], df[y].values[1:]

    if y=='Del':
        y='\u03B4'
    elif y=='dDel/dt':
        y='d\u03B4/dt'

    layout = go.Layout(
        plot_bgcolor="#FFF",
        xaxis=dict(
            title=df.index.name+' (min)',
            linecolor="#BCCCDC",
            linewidth=2,
            gridcolor="#BCCCDC",
            zeroline = False
        ),
        yaxis=dict(
            title=y,  
            linecolor="#BCCCDC", 
            linewidth=2,
            gridcolor="#BCCCDC",
            zeroline = False
        )
    )

    fig = go.Figure(
        data = go.Scatter(x=x_scat, y=y_scat, marker_color='green', mode='lines+markers'),
        layout = layout
    )
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

def save_file(name, content):
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join('./temp', name), "wb") as fp:
        fp.write(base64.decodebytes(data))

def uploaded_files():
    files = []
    for filename in os.listdir('./temp'):
        path = os.path.join('./temp', filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


