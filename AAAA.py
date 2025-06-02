import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from pypmml import Model

class PMMLApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧑‍⚕ Recomendación Médica con PMML")
        self.root.geometry("600x700")
        self.root.configure(bg="#f0f4f8")

        self.model = None
        self.fields_info = {}
        self.widgets = {}

        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Personalización de estilos ttk
        self.style.configure('TFrame', background="#f0f4f8")
        self.style.configure('TLabel', background="#f0f4f8", font=('Segoe UI', 11))
        self.style.configure('Header.TLabel', font=('Segoe UI Semibold', 20), background="#f0f4f8", foreground="#006633")
        self.style.configure('SubHeader.TLabel', font=('Segoe UI', 13), background="#f0f4f8", foreground="#004d26")
        self.style.configure('TButton', font=('Segoe UI Semibold', 12), foreground="white", background="#006633")
        self.style.map('TButton',
                       background=[('active', '#004d26'), ('!disabled', '#006633')])

        self.create_widgets()

    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(pady=15, padx=15, fill='x')

        title = ttk.Label(header_frame, text="Recomendación Médica de Lentes", style='Header.TLabel')
        title.pack()

        subtitle = ttk.Label(header_frame, text="Carga tu modelo PMML y realiza predicciones fácilmente",
                             style='SubHeader.TLabel')
        subtitle.pack(pady=(5, 15))

        # Cargar modelo
        load_frame = ttk.Frame(self.root)
        load_frame.pack(pady=(0, 10), padx=15, fill='x')

        self.load_btn = ttk.Button(load_frame, text="📂 Cargar Modelo PMML", command=self.load_pmml)
        self.load_btn.pack(fill='x')

        # Contenedor campos dinámicos
        self.fields_frame = ttk.Frame(self.root)
        self.fields_frame.pack(pady=10, padx=15, fill='both', expand=True)

        # Scrollbar para campos si hay muchos
        self.canvas = tk.Canvas(self.fields_frame, bg="#f0f4f8", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.fields_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Botón predecir
        self.predict_btn = ttk.Button(self.root, text="🔮 Predecir", command=self.predict, state='disabled')
        self.predict_btn.pack(pady=15, padx=15, fill='x')

        # Resultado
        self.result_label = ttk.Label(self.root, text="", font=('Segoe UI Semibold', 14), foreground="#004d26",
                                      background="#f0f4f8", anchor='center')
        self.result_label.pack(pady=(5, 20), padx=15, fill='x')

    def load_pmml(self):
        file_path = filedialog.askopenfilename(filetypes=[("PMML Files", "*.pmml")])
        if not file_path:
            return

        try:
            self.model = Model.fromFile(file_path)

            tree = ET.parse(file_path)
            root = tree.getroot()
            ns = {'pmml': 'http://www.dmg.org/PMML-4_2'}

            mining_schema = root.find('pmml:TreeModel/pmml:MiningSchema', ns)
            input_fields = []
            for mf in mining_schema.findall('pmml:MiningField', ns):
                usageType = mf.get('usageType', 'active')
                if usageType != 'target':
                    input_fields.append(mf.get('name'))

            data_dictionary = root.find('pmml:DataDictionary', ns)

            self.fields_info.clear()
            for df in data_dictionary.findall('pmml:DataField', ns):
                name = df.get('name')
                if name not in input_fields:
                    continue

                optype = df.get('optype')
                dataType = df.get('dataType')

                info = {'optype': optype, 'dataType': dataType}

                values = [v.get('value') for v in df.findall('pmml:Value', ns)]
                if values:
                    info['values'] = values

                intervals = df.findall('pmml:Interval', ns)
                if intervals:
                    iv = intervals[0]
                    info['interval'] = {
                        'leftMargin': iv.get('leftMargin'),
                        'rightMargin': iv.get('rightMargin'),
                        'closure': iv.get('closure')
                    }

                self.fields_info[name] = info

            self.build_input_fields()
            self.result_label.config(text="Modelo cargado correctamente. ¡Listo para predecir!")
            self.predict_btn.config(state='normal')
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el modelo:\n{e}")

    def build_input_fields(self):
        # Limpiar viejos widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.widgets.clear()

        for field, info in self.fields_info.items():
            label = ttk.Label(self.scrollable_frame, text=field + ":")
            label.pack(anchor='w', pady=(10, 2))

            if info['optype'] == 'categorical' and 'values' in info:
                combo = ttk.Combobox(self.scrollable_frame, values=info['values'], state='readonly', font=('Segoe UI', 11))
                combo.pack(fill='x')
                self.widgets[field] = combo

                hint = "Opciones válidas: " + ", ".join(info['values'])
                hint_label = ttk.Label(self.scrollable_frame, text=hint, font=("Segoe UI", 8), foreground="gray")
                hint_label.pack(anchor='w', padx=5, pady=(0, 5))

            elif info['optype'] == 'continuous':
                entry = ttk.Entry(self.scrollable_frame, font=('Segoe UI', 11))
                entry.pack(fill='x')
                self.widgets[field] = entry

                if 'interval' in info:
                    iv = info['interval']
                    hint = f"Rango válido: {iv['leftMargin']} a {iv['rightMargin']} ({iv['closure']})"
                else:
                    hint = "Ingrese número decimal"

                hint_label = ttk.Label(self.scrollable_frame, text=hint, font=("Segoe UI", 8), foreground="gray")
                hint_label.pack(anchor='w', padx=5, pady=(0, 5))

            else:
                entry = ttk.Entry(self.scrollable_frame, font=('Segoe UI', 11))
                entry.pack(fill='x')
                self.widgets[field] = entry
                hint_label = ttk.Label(self.scrollable_frame, text="Ingrese valor", font=("Segoe UI", 8), foreground="gray")
                hint_label.pack(anchor='w', padx=5, pady=(0, 5))

    def predict(self):
        if not self.model:
            messagebox.showwarning("Modelo no cargado", "Primero carga un modelo PMML.")
            return

        try:
            data = {}
            for field, widget in self.widgets.items():
                val = widget.get()
                if not val:
                    raise ValueError(f"Debe ingresar un valor para '{field}'")

                if self.fields_info[field]['optype'] == 'continuous':
                    try:
                        val = float(val)
                    except ValueError:
                        raise ValueError(f"El campo '{field}' debe ser un número válido")

                data[field] = [val]

            df = pd.DataFrame(data)
            result = self.model.predict(df)

            output_col = self.model.outputNames[0] if self.model.outputNames else result.columns[-1]
            pred = result[output_col].iloc[0]

            self.result_label.config(text=f"Resultado: {pred}", foreground="#006633")

        except Exception as e:
            messagebox.showerror("Error en predicción", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = PMMLApp(root)
    root.mainloop()
