# Marcador de tweets 
Para ejecutar esta aplicación es necesario que cuente con [Anaconda](https://www.anaconda.com/products/individual#Downloads), [git](https://git-scm.com/downloads) y [Postgres](https://www.postgresql.org/download/) instalados en su computador. En caso de que tenga un sistema operativo **macOS**, puede realizar la instalación de git y postgres a través de [brew](https://brew.sh/) usando los comandos `brew install postgresql` y `brew install git`. Luego puede proceder con los siguientes pasos.

1. Abrir la consola y entrar a la carpeta donde desea alojar este repositorio. Un ejemplo en Windows sería: `cd "C:\Users\User\Downloads"`.
3. Clonar el repositorio a través del comando: `git clone https://github.com/lgomezt/marcacion_tweets.git`.
4. Una vez en la carpeta debe crear un archivo llamado `database.ini` y alojarlo en la misma carpeta en la que se encuentre el archivo `run.py`. El archivo se puede crear desde el Notepad y debe tener la siguiente estructura:

```
[postgresql]
host = .
database = .
port = .
user = .
password = .
```

Deberá reemplazar los puntos con la información de las credencial para acceder a la base de datos en PostgreSQL. No olvide incluir la línea `[postgresql]` en su archivo `database.ini`. Asegurese que la extensión del archivo sea `.ini` y no `.txt`.

4. Ahora vamos a crear un ambiente donde vamos a ejecutar la aplicación. En la consola escriba el comando `conda create -n "semillero_redes" python=3.9.7 ipython`.
5. Desde la terminal activamos el ambiente escribiendo: `conda activate semillero_redes`.
6. Procedemos a instalar los paquetes necesarios: `pip install -r requirements.txt`.
7. Solo queda ejecutar la herramienta escribiendo: `python run.py`
8. Espere hasta que en su consola salga un mensaje diciendo `* Running on http://127.0.0.1:8050/`. Cuando eso suceda, ingrese la ruta `http://127.0.0.1:8050/` en su navegador para interactuar con el aplicativo.

