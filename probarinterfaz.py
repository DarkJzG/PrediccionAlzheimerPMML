import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
from pypmml import Model

modelo = None
input_fields = []

def seleccionar_archivo_pmml():
    ruta = filedialog.askopenfilename(filetypes=[("PMML files", "*.pmml")])
    if not ruta:
        return
    try:
        global modelo
        modelo = Model.load(ruta)
        messagebox.showinfo("Modelo cargado", f"Modelo cargado desde:\n{ruta}")
        mostrar_interfaz_dinamica()
    except Exception as e:
        messagebox.showerror("Error al cargar modelo", str(e))

def mostrar_interfaz_dinamica():
    global input_fields

    # Obtener variables de entrada requeridas
    input_fields = list(modelo.inputNames)
    valores = {}

    # Crear ventana dinámica
    ventana = tk.Tk()
    ventana.title("Predicción con PMML")
    ventana.geometry("400x500")

    combos = {}

    for campo in input_fields:
        tk.Label(ventana, text=f"{campo}:").pack()
        combo = ttk.Combobox(ventana)
        combo.pack()
        combos[campo] = combo

    resultado_label = tk.Label(ventana, text="Resultado: ")
    resultado_label.pack(pady=10)

    def predecir():
        datos = {}
        for campo in input_fields:
            valor = combos[campo].get()
            if not valor:
                messagebox.showwarning("Campo vacío", f"Por favor completa el campo: {campo}")
                return
            datos[campo] = valor

        df = pd.DataFrame([datos])
        try:
            pred = modelo.predict(df)
            # Detectar la columna de salida (target)
            output_column = list(modelo.targetNames)[0]
            resultado_texto = pred[output_column].values[0]
            resultado_label.config(text=f"Resultado: {resultado_texto}")

        except Exception as e:
            messagebox.showerror("Error al predecir", str(e))

    tk.Button(ventana, text="Predecir", command=predecir).pack(pady=10)
    ventana.mainloop()

# Ventana inicial
inicio = tk.Tk()
inicio.title("Cargar modelo PMML")
inicio.geometry("300x150")

tk.Label(inicio, text="Selecciona tu archivo PMML").pack(pady=20)
tk.Button(inicio, text="Cargar modelo", command=seleccionar_archivo_pmml).pack()

inicio.mainloop()
