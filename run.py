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
from datetime import date
import psycopg2
from configparser import ConfigParser
import getpass
import socket
from IPython.core.debugger import Pdb
ipdb = Pdb()

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
sql = False # Decidimos de donde sacar los datos
if sql:
    query = "SELECT id, tweet_text FROM public.tweet;"
    credenciales = config()
    conexion = psycopg2.connect(**credenciales)
    tweets = pd.read_sql_query(sql = query, con = conexion)

    # Nos quedamos solo con las columnas necesarias
    tweets = tweets[["id", "tweet_text"]]
    # Usamos expresiones regulares para quitar los textos de los retweets
    tweets["tweet_text"] = tweets["tweet_text"].apply(lambda x: re.sub("RT @.+: ", "", x))
    # Eliminamos tweets duplicados
    tweets = tweets.drop_duplicates("tweet_text").reset_index(drop = True)
else:
    path = r"C:\Users\User\OneDrive - Universidad de los Andes\Asistencia de investigacion\Twitter\App\\"
    tweets = pd.read_pickle(path + "random_sample.gzip",
        compression = "gzip")
    tweets.columns = ["id", "tweet_text"]
    hoy = str(date.today())
    try:
        resultados = pd.read_pickle(path + "resultados-" + hoy + ".gzip",
            compression = "gzip")
    except:
        resultados = pd.DataFrame() # Creamos un dataframe pa guardar los resultados

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.CYBORG])
server = app.server

# Elementos layout
logo = "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.stickpng.com%2Fes%2Fimg%2Ficonos-logotipos-emojis%2Fcompanias-technologicas%2Flogo-twitter&psig=AOvVaw29Fw4TRGP1nBTMdqKu_X5T&ust=1637993456782000&source=images&cd=vfe&ved=0CAsQjRxqFwoTCKDzyravtfQCFQAAAAAdAAAAABAD"
navbar = dbc.Navbar([
    html.A(
        dbc.Row([
            dbc.Col(html.Img(src = logo, height = "30px")), #"http://assets.stickpng.com/images/580b57fcd9996e24bc43c53e.png"
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
    dbc.Row([
        dbc.Col(
            html.P("Si deseas participar en una rifa por tu participación, dejanos tu correo a continuación:")
        ),
        dbc.Col(
            html.Div([
            dcc.Input(
                id = "correo",
                type = "email",
                placeholder = "¿Cuál es tu correo?",
                style = {'textAlign': 'center', 'width': '100%'})
            ])
        )
    ])
], style = {'padding': '10px 60px 30px'})

mensaje = "De las opciones presentadas a continuación, seleccione la que crea que describe mejor el mensaje presentado."
instrucciones = html.Div([
    html.H5(mensaje, style = {'textAlign': 'justify'}),
    # Guardamos el índice de la fila, pero no lo mostramos
    html.Div(id = 'fila', style= {'display': 'None'})
    ], style = {'padding': '10px 60px 10px'})

botones = html.Div([
    dbc.Row([
        dbc.Col(dbc.Button('Izquierda', id = 'izquierda', color = "primary", block = True)),
        dbc.Col(dbc.Button('Centro', id = 'centro', color = "primary", block = True)),
        dbc.Col(dbc.Button('Derecha', id = 'derecha', color = "primary", block = True)),
        dbc.Col(dbc.Button('No tengo idea', id = 'no_idea', color = "primary", block = True)),
        dbc.Col(dbc.Button('No aplica o es un error', id = 'no_aplica', color = "primary", block = True))
        ])
], style = {'padding': '10px 60px 10px'})

# Definimos layout
app.layout = html.Div(children = [navbar, texto, instrucciones, botones])

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

# Función para subir resultados a nuestra base message en postgres
def guardar_resultado(fila, sql):
    """
    Usamos esta función para cargar la votación del usuario en la base de datos message.
    El parámetro fila debe ser una tupla que contenga 5 valores que hacen alusión a las variables
    usuario1, usuario2, id_tweet, marca y fecha.
    """
    # Si usamos sql, guardar los resultados en sql. Si no, guardarlos en local
    if sql:
        try:
            # Cargamos los resultados en la base message
            credenciales = config(filename = 'database.ini', section = 'postgresql')
            conexion = psycopg2.connect(**credenciales)
            # Creamos un cursor para editar la base
            cursor = conexion.cursor()

            # Insertamos una fila
            query = """INSERT INTO message (usuario1, usuario2, correo, id_tweet, marca, fecha) VALUES (%s, %s, %s, %s, %s, %s);"""
            cursor.execute(query, fila)
            conexion.commit()
            
            count = cursor.rowcount
            print(count, "Se ingresó la fila", fila)

            if conexion:
                cursor.close()
                conexion.close()

        except (Exception, psycopg2.Error) as error:
            print("No se pudo ingresar la fila", error)
    else:
        global resultados # Pesima práctica de programación pero toca
        fila = pd.DataFrame(fila).T
        fila.columns = ["usuario1", "usuario2", "correo", "id_tweet", "marca", "fecha"]
        resultados = resultados.append(fila).reset_index(drop = True)
        hoy = str(date.today())
        resultados.to_pickle(path + "resultados-" + hoy + ".gzip",
            compression = "gzip")

# Cambiar de texto cuando se presione algún botón y guardar resultados.
@app.callback(Output('texto_tweet', 'children'),
              Output('fila', 'children'),
              Input('izquierda', 'n_clicks'),
              Input('centro', 'n_clicks'),
              Input('derecha', 'n_clicks'),
              Input('no_idea', 'n_clicks'),
              Input('no_aplica', 'n_clicks'),
              Input('correo', "value"),
              Input('fila', 'children'),
              )
def cambiar_texto(izq, cen, der, no_idea, no_aplica, correo, fila):
    # Cuando inicia la app se escoge un texto al azar
    if (izq is None) & (cen is None) & (der is None) & (no_idea is None) & (no_aplica is None) & (correo is None):
        fila = random.randint(0, tweets.shape[0])
        tweet = tweets.iloc[fila].tweet_text
        return(tweet, fila)
    
    # Se guarda la clasificación del usuario
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

    # Guardamos los resultados en una tupla 
    usuario1 = get_ip()
    usuario2 = getpass.getuser()
    correo = str(correo)
    id_tweet = str(tweets.iloc[fila].id)
    marca = str(valor)
    fecha = str(datetime.now())
    resultado = (usuario1, usuario2, correo, id_tweet, marca, fecha)
    
    # Subir resultados a nuestra base message en postgres 
    guardar_resultado(fila = resultado, sql = sql)

    # Cambiamos el texto
    fila = random.randint(0, tweets.shape[0])
    tweet = tweets.iloc[fila].tweet_text

    return(tweet, fila)

if __name__ == "__main__":
    app.run_server()