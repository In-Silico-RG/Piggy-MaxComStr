import requests
from bs4 import BeautifulSoup
import re
import os

# Lista de URLs
urls = [
    "https://www.genome.jp/tools-bin/search_list?STEP=50&PAGETEXT=1&hPAR=20&hPAGE=1&unclassified=&org_name=ko&warning=yes&allch=10&ckid=C17754&ckid=C08557&ckid=C08556&ckid=C08543&ckid=C17757&ckid=C08565&ckid=C17753&ckid=C08560&ckid=C08539&ckid=C08548&PAGETEXT2=1&ENTRY=&PID=1943210&TARGET=STR&PROGRAM=SIMCOMP&SHOW=structure&DATABASE=compound&smiles=0&LANG=",
"https://www.genome.jp/tools-bin/search_list?STEP=50&PAGETEXT=1&hPAR=20&hPAGE=2&unclassified=&org_name=ko&warning=yes&allch=10&ckid=C17754&ckid=C08557&ckid=C08556&ckid=C08543&ckid=C17757&ckid=C08565&ckid=C17753&ckid=C08560&ckid=C08539&ckid=C08548&PAGETEXT2=1&ENTRY=&PID=1943210&TARGET=STR&PROGRAM=SIMCOMP&SHOW=structure&DATABASE=compound&smiles=0&LANG=",
"https://www.genome.jp/tools-bin/search_list?STEP=50&PAGETEXT=2&hPAR=20&hPAGE=3&unclassified=&org_name=ko&warning=yes&allch=10&PAGETEXT2=2&ENTRY=&PID=1943210&TARGET=STR&PROGRAM=SIMCOMP&SHOW=structure&DATABASE=compound&smiles=0&LANG=",
"https://www.genome.jp/tools-bin/search_list?STEP=50&PAGETEXT=3&hPAR=20&hPAGE=4&unclassified=&org_name=ko&warning=yes&allch=10&PAGETEXT2=3&ENTRY=&PID=1943210&TARGET=STR&PROGRAM=SIMCOMP&SHOW=structure&DATABASE=compound&smiles=0&LANG=",
"https://www.genome.jp/tools-bin/search_list?STEP=50&PAGETEXT=4&hPAR=20&hPAGE=5&unclassified=&org_name=ko&warning=yes&allch=10&PAGETEXT2=4&ENTRY=&PID=1943210&TARGET=STR&PROGRAM=SIMCOMP&SHOW=structure&DATABASE=compound&smiles=0&LANG=",
"https://www.genome.jp/tools-bin/search_list?STEP=50&PAGETEXT=5&hPAR=20&hPAGE=6&unclassified=&org_name=ko&warning=yes&allch=10&PAGETEXT2=5&ENTRY=&PID=1943210&TARGET=STR&PROGRAM=SIMCOMP&SHOW=structure&DATABASE=compound&smiles=0&LANG="

    # Agrega más URLs aquí
]

# Crear carpeta para almacenar los resultados
carpeta_salida = "/home/angel/Escritorio/Betaxantina_identificadores"
os.makedirs(carpeta_salida, exist_ok=True)

# Archivo donde se guardarán los identificadores
ruta_archivo = os.path.join(carpeta_salida, "identificadores.txt")

# Set para evitar duplicados
todos_identificadores = set()

# Extraer identificadores de cada URL
for url in urls:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    identificadores = re.findall(r'C\d{5}', soup.text)
    todos_identificadores.update(identificadores)

# Guardar los identificadores en el archivo
with open(ruta_archivo, "w") as file:
    for identificador in sorted(todos_identificadores):
        file.write(identificador + "\n")

print("Identificadores guardados en:", ruta_archivo)
