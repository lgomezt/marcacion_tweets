import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from IPython.core.debugger import set_trace

import pandas as pd
import re
import random
from datetime import datetime
import psycopg2
from configparser import ConfigParser
import getpass
import socket

# Por seguridad no queremos que las credenciales de nuestra base estén directamente escritas 
# en el script. Del mismo modo, quisieramos que si cambiamos de servidores, no sea necesario
# modificar el código. Por tal motivo creamos una función para leer un archivo que estará 
# alojado localmente en el pc de cada investigador con la información de acceso al servidor.

def config(filename = 'database.ini', section = 'postgresql'):
    """ Función para cargar nuestras credenciales para acceder a nuestra base de datos"""
    # Abrimos el archivo especificado en el parámetro filename
    parser = ConfigParser()
    parser.read(filename)

    # Creamos un diccionario a partir de la sección escogida en el parámetro section
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

# Importamos los tweets
query = "SELECT * FROM public.tweet;"
credenciales = config()
conexion = psycopg2.connect(**credenciales)
tweets = pd.read_sql_query(sql = query, con = conexion)

# Nos quedamos solo con las columnas necesarias
tweets = tweets[["id", "tweet_text"]]
# Usamos expresiones regulares para quitar los textos de los retweets
tweets["tweet_text"] = tweets["tweet_text"].apply(lambda x: re.sub("RT @.+: ", "", x))
# Eliminamos tweets duplicados
tweets = tweets.drop_duplicates("tweet_text").reset_index(drop = True)

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.CYBORG])
server = app.server

# Elementos layout
navbar = dbc.Navbar([
    html.A(
        dbc.Row([
            dbc.Col(html.Img(src = "http://assets.stickpng.com/images/580b57fcd9996e24bc43c53e.png", height = "30px")),
            dbc.Col(dbc.NavbarBrand("Clasificador de tweets"))
        ]),
        href = "https://sites.google.com/site/tomasrodriguezbarraquer/"
        )
    ],
    color = "dark",
    dark = True,
)

texto = html.Div([
    dbc.Row([
        dbc.Col(html.H3(id = "texto_tweet", style = {'textAlign': 'center'}))
        ], justify = "center", align = "center"),
], style = {'padding': '10px 60px 30px'})

mensaje = "De las opciones presentadas a continuación, seleccione la que crea que describe mejor el mensaje presentado."
instrucciones = html.Div([
    html.H5(mensaje, style = {'textAlign': 'justify'})
    ], style = {'padding': '10px 60px 10px'})

botones = html.Div([
    dbc.Row([
        dbc.Col(dbc.Button('Izquierda', id = 'izquierda', color = "primary", block = True)),
        dbc.Col(dbc.Button('Centro', id = 'centro', color = "primary", block = True)),
        dbc.Col(dbc.Button('Derecha', id = 'derecha', color = "primary", block = True)),
        dbc.Col(dbc.Button('No tengo idea', id = 'no_idea', color = "primary", block = True)),
        dbc.Col(dbc.Button('No aplica', id = 'no_aplica', color = "primary", block = True))
        ])
], style = {'padding': '10px 60px 10px'})

# Definimos layout
app.layout = html.Div(children = [navbar, texto, instrucciones, botones, dcc.Store(id = 'Resultados')])

# Callbacks

# Función para identificar la IP del usuario
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# Cambiar de texto cuando se presione algún botón y guardar resultados.
@app.callback(Output('texto_tweet', 'children'),
              Output('Resultados', 'data'),
              Input('izquierda', 'n_clicks'),
              Input('centro', 'n_clicks'),
              Input('derecha', 'n_clicks'),
              Input('no_idea', 'n_clicks'),
              Input('no_aplica', 'n_clicks'),
              Input('Resultados', 'data'),
              )
def cambiar_texto(izq, cen, der, no_idea, no_aplica, resultados):
    if (izq is None) & (cen is None) & (der is None) & (no_idea is None) & (no_aplica is None):
        fila = random.randint(0, tweets.shape[0])
        tweet = tweets.iloc[fila].tweet_text
        resultados = pd.DataFrame()
        return(tweet, resultados.to_json(orient = 'split'))
    
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'izquierda' in changed_id:
        valor = -1
    elif 'centro' in changed_id:
        valor = 0
    elif 'derecha' in changed_id:
        valor = 1
    elif 'no_idea' in changed_id:
        valor = "no_idea"
    elif 'no_aplica' in changed_id:
        valor = "no_aplica"

    fila = random.randint(0, tweets.shape[0])
    tweet = tweets.iloc[fila].tweet_text

    if resultados is None:
        resultados = pd.DataFrame()
    else:
        resultados = pd.read_json(resultados, orient = 'split')

    resultado = pd.DataFrame({
        "usuario1": get_ip(),
        "usuario2": getpass.getuser(), 
        "id_tweet": tweets.iloc[fila].id,
        "marca": valor,
        "hora": datetime.now()
        }, index = [0])

    resultados = pd.concat([resultados, resultado], axis = 0).reset_index(drop = True)

    return(tweet, resultados.to_json(orient = 'split'))

if __name__ == "__main__":
    app.run_server(debug = True)