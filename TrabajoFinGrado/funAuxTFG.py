import os
import json
import tkinter as tk
from tkinter import filedialog

def guardar_informacion(info):
    """
    Guarda la información recibida en un archivo JSON dentro de la carpeta 'guardados'.
    
    Parámetros:
        info: La información a guardar (puede ser un diccionario, lista, etc.).
    """
    # Definir la carpeta donde se guardarán los archivos
    carpeta_guardados = os.path.join(os.getcwd(), "guardados")
    
    # Crear la carpeta si no existe
    if not os.path.exists(carpeta_guardados):
        os.makedirs(carpeta_guardados)
    
    # Configurar la ventana de Tkinter (oculta)
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal

    # Abrir el cuadro de diálogo para elegir el nombre y ubicación del archivo.
    ruta_archivo = filedialog.asksaveasfilename(
        initialdir=carpeta_guardados,
        title="Guardar información",
        defaultextension=".json",  # Se cambia la extensión a JSON
        filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
    )

    # Si el usuario seleccionó una ruta, se guarda la información.
    if ruta_archivo:
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
                json.dump(info, archivo, indent=4, ensure_ascii=False)  # Guardar en formato JSON
            print("Información guardada en:", ruta_archivo)
        except Exception as e:
            print("Ocurrió un error al guardar la información:", e)
    else:
        print("Operación cancelada. No se guardó ningún archivo.")



def cargar_informacion():
    """
    Carga la información de un archivo JSON seleccionado por el usuario, ubicado dentro de la carpeta 'guardados'.
    
    Retorna:
        La información cargada, o None si la operación se canceló o ocurrió un error.
    """
    # Definir la carpeta donde se encuentran los archivos guardados
    carpeta_guardados = os.path.join(os.getcwd(), "guardados")
    
    # Configurar la ventana de Tkinter (oculta)
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal

    # Abrir el cuadro de diálogo para elegir el archivo a cargar.
    ruta_archivo = filedialog.askopenfilename(
        initialdir=carpeta_guardados,
        title="Seleccionar archivo para cargar",
        filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
    )

    # Si el usuario seleccionó un archivo, se procede a cargar la información.
    if ruta_archivo:
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                data = json.load(archivo)
            print("Información cargada exitosamente desde:", ruta_archivo)
            return data
        except Exception as e:
            print("Ocurrió un error al cargar la información:", e)
            return None
    else:
        print("Operación cancelada. No se cargó ningún archivo.")
        return None

