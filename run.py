import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from IPython.core.debugger import set_trace

import os
import pandas as pd
import re
import random
from datetime import datetime

path_data = os.getcwd() + "/data/"

# Importamos los tweets
tweets = pd.read_csv(path_data + "all_tweets.csv")
# Nos quedamos con las columnas importantes
tweets = tweets[["ID", "Text"]]
# Usamos expresiones regulares para quitar los textos de los retweets
tweets["Text"] = tweets["Text"].apply(lambda x: re.sub("RT @.+: ", "", x))
# Eliminamos tweets duplicados
tweets = tweets.drop_duplicates("Text").reset_index(drop = True)


app = dash.Dash(__name__, __name__external_stylesheets = [dbc.themes.CYBORG])
server = app.server

navbar = dbc.Navbar([
    html.A(
        dbc.Row(dbc.Col(dbc.NavbarBrand("Título de la app"))),
        href = "https://sites.google.com/site/tomasrodriguezbarraquer/"
        )
    ],
    color = "dark",
    dark = True,
)
    
texto = html.Div([
    dbc.Row([
        dbc.Col(html.H3(id = "texto_tweet", style = {'textAlign': 'justify'}))
        ], justify = "center", align = "center")
], style = {'padding': '50px 50px 50px 10px'})

botones = html.Div([
    dbc.Row([
        dbc.Col(dbc.Button('Izquierda', id = 'izquierda', color = "primary", block = True)),
        dbc.Col(dbc.Button('Centro', id = 'centro', color = "primary", block = True)),
        dbc.Col(dbc.Button('Derecha', id = 'derecha', color = "primary", block = True))
        ])
], style = {'padding': '10px 50px 50px 50px'})

# Cambiar de texto cuando se presione algún botón
@app.callback(Output('texto_tweet', 'children'),
              Output('Resultados', 'data'),
              Input('izquierda', 'n_clicks'),
              Input('centro', 'n_clicks'),
              Input('derecha', 'n_clicks'),
              Input('Resultados', 'data'))
def cambiar_texto(izq, cen, der, resultados):
    if (izq is None) & (cen is None) & (der is None):
        fila = random.randint(0, tweets.shape[0])
        tweet = tweets.iloc[fila].Text
        resultados = pd.DataFrame()
        return(tweet, resultados.to_json(orient = 'split'))
    
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'izquierda' in changed_id:
        valor = -1
    elif 'centro' in changed_id:
        valor = 0
    elif 'derecha' in changed_id:
        valor = 1

    fila = random.randint(0, tweets.shape[0])
    tweet = tweets.iloc[fila].Text

    if resultados is None:
        resultados = pd.DataFrame()
    else:
        resultados = pd.read_json(resultados, orient = 'split')

    resultado = pd.DataFrame({
        "usuario": "admin", 
        "id_tweet": tweets.iloc[fila].ID,
        "marca": valor,
        "hora": datetime.now()
        }, index = [0])

    resultados = pd.concat([resultados, resultado], axis = 0).reset_index(drop = True)

    return(tweet, resultados.to_json(orient = 'split'))

app.layout = html.Div(children = [navbar, texto, botones, dcc.Store(id = 'Resultados')])

if __name__ == "__main__":
    app.run_server()

app.layout = html.Div(children = [navbar, texto, botones, dcc.Store(id = 'Resultados')])

if __name__ == "__main__":
    app.run_server(debug = True)