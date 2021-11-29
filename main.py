""" Importamos el modelo del archivo en que lo definimos. """
from model_robots import StorageModel

""" matplotlib lo usaremos crear una animación de cada uno de los pasos
    del modelo. """
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
plt.rcParams["animation.html"] = "jshtml"
matplotlib.rcParams['animation.embed_limit'] = 2**128

""" Importamos los siguientes paquetes para el mejor manejo de valores
    numéricos."""
import numpy as np
import pandas as pd

""" Definimos otros paquetes que vamos a usar para medir el tiempo de
    ejecución de nuestro algoritmo. """
import time
import datetime


M = int(input("dame el numero de filas "))

N = int(input("deme el numero de columnas "))

numAgents = int(input("Dame el numero de Agentes "))

numBoxes = int(input("Dame el numero de Cajas "))

MAXTIME = int(input("Tiempo máximo de ejecución en segundos "))

""" Registramos el tiempo de inicio y ejecutamos la simulación. """
start_time = time.time()
model = StorageModel(M, N,numAgents,numBoxes)

frames =-1
while datetime.timedelta(seconds=(time.time() - start_time)< MAXTIME):
    frames+=1
    if model.unsortedBoxes==0:
        break
    model.step()

print('Tiempo de ejecución:', str(datetime.timedelta(seconds=(time.time() - start_time))))
print('Número de movimientos realizados por todos los agentes', model.agentMovements)

""" Obtenemos la información que almacenó el colector, este nos entregará un
    DataFrame de pandas que contiene toda la información. """
all_grid = model.datacollector.get_model_vars_dataframe()

# Graficamos la información usando `matplotlib`
fig, axs = plt.subplots(figsize=(7,7))
axs.set_xticks([])
axs.set_yticks([])
patch = plt.imshow(all_grid.iloc[0][0])

def animate(i):
    patch.set_data(all_grid.iloc[i][0])

anim = animation.FuncAnimation(fig, animate, frames=frames,interval=1)
plt.show()