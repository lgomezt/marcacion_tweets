# Marcador de tweets 
Para ejecutar esta aplicación es necesario que cuente con [Anaconda](https://www.anaconda.com/products/individual#Downloads) y [git](https://git-scm.com/downloads) instalados en su computador. Luego puede proceder con los siguientes pasos.

1. Abrir la consola y entrar a la carpeta donde desea alojar este repositorio. Un ejemplo en Windows sería: `cd "C:\Users\User\Downloads"`.
2. Clonar el repositorio a través del comando: `git clone https://github.com/lgomezt/marcacion_tweets.git`.
3. Una vez en la carpeta debe crear un archivo llamado `database.ini` y alojarlo en la misma carpeta en la que se encuentre el archivo `run.py`. El archivo se puede crear desde el Notepad y debe tener la siguiente estructura:

```
[postgresql]
host = .
database = .
port = .
user = .
password = .
```

Deberá reemplazar los puntos con la información de las credencial para acceder a la base de datos en PostgreSQL. No olvide incluir la línea `[postgresql]` en su archivo `database.ini`.

4. Ahora vamos a crear un ambiente donde vamos a ejecutar la aplicación. En la consola escriba el comando `conda create -n "semillero_redes" python=3.9.7 ipython`.
5. Desde la terminal activamos el ambiente escribiendo: `conda activate semillero_redes`.
6. Procedemos a instalar los paquetes necesarios: `pip install requirements.txt`.
7. Solo queda ejecutar la herramienta escribiendo: `python run.py`


