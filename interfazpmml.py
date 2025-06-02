import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from pypmml import Model

# Variable global para el modelo
modelo = None

def seleccionar_pmml():
    ruta = filedialog.askopenfilename(filetypes=[("PMML files", "*.pmml")])
    if not ruta:
        return

    try:
        global modelo
        modelo = Model.load(ruta)
        messagebox.showinfo("Éxito", "Modelo cargado correctamente.")
        mostrar_interfaz_prediccion()
    except Exception as e:
        messagebox.showerror("Error al cargar el modelo", str(e))

def mostrar_interfaz_prediccion():
    ventana = tk.Tk()
    ventana.title("Predicción de uso de lentes")
    ventana.geometry("350x300")

    tk.Label(ventana, text="Edad:").pack()
    combo_edad = ttk.Combobox(ventana, values=["joven", "pre-presbicia", "presbicia"])
    combo_edad.pack()

    tk.Label(ventana, text="Presión ocular:").pack()
    combo_presion = ttk.Combobox(ventana, values=["normal", "alta"])
    combo_presion.pack()

    tk.Label(ventana, text="Diagnóstico:").pack()
    combo_diag = ttk.Combobox(ventana, values=["miope", "hipermétrope"])
    combo_diag.pack()

    resultado = tk.Label(ventana, text="Resultado: ")
    resultado.pack()

    def predecir():
        if not modelo:
            messagebox.showerror("Error", "No se ha cargado el modelo.")
            return

        edad = combo_edad.get()
        presion = combo_presion.get()
        diagnostico = combo_diag.get()

        if not edad or not presion or not diagnostico:
            messagebox.showwarning("Datos faltantes", "Completa todos los campos.")
            return

        try:
            df = pd.DataFrame([{
                "edad": edad,
                "presion": presion,
                "diagnostico": diagnostico
            }])
            pred = modelo.predict(df)
            resultado.config(text=f"Resultado: {pred.iloc[0, -1]}")
        except Exception as e:
            messagebox.showerror("Error en predicción", str(e))

    tk.Button(ventana, text="Predecir", command=predecir).pack(pady=10)
    ventana.mainloop()

# Ventana principal para seleccionar archivo
ventana_inicio = tk.Tk()
ventana_inicio.title("Cargar modelo PMML")
ventana_inicio.geometry("300x150")

tk.Label(ventana_inicio, text="Selecciona tu archivo .pmml").pack(pady=20)
tk.Button(ventana_inicio, text="Cargar modelo", command=seleccionar_pmml).pack()

ventana_inicio.mainloop()
