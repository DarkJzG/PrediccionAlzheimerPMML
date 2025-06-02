import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from pypmml import Model
from PIL import Image, ImageTk
import webbrowser


class PMMLApp:
    def __init__(self, root):
        self.root = root
        self.root.title("👁 VISOR-PMML: Sistema de Predicción")
        self.root.geometry("900x950")
        self.root.configure(bg="#ffffff")
        self.root.resizable(True, True)

        # Variable para controlar actualización del slider
        self.updating_slider = False

        # Configuración de estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Colores
        self.bg_color = "#ffffff"
        self.primary_color = "#00a8ff"
        self.secondary_color = "#ff4757"
        self.text_color = "#2f3542"
        self.card_color = "#f1f2f6"
        self.highlight_color = "#dfe4ea"

        # Configurar estilos
        self.configure_styles()

        self.model = None
        self.fields_info = {}
        self.widgets = {}

        self.create_main_container()
        self.create_header()
        self.create_load_section()
        self.create_fields_container()
        self.create_result_section()
        self.create_footer()

    def configure_styles(self):
        """Configura todos los estilos para la interfaz"""
        self.style.configure('.', background=self.bg_color, foreground=self.text_color)

        # Frame styles
        self.style.configure('Card.TFrame', background=self.card_color, relief=tk.RAISED, borderwidth=0)

        # Label styles
        self.style.configure('Title.TLabel',
                             font=('Segoe UI', 24, 'bold'),
                             foreground=self.primary_color,
                             background=self.bg_color)
        self.style.configure('Subtitle.TLabel',
                             font=('Segoe UI', 12),
                             foreground="#57606f",
                             background=self.bg_color)
        self.style.configure('Field.TLabel',
                             font=('Segoe UI', 10, 'bold'),
                             foreground=self.text_color,
                             background=self.card_color)
        self.style.configure('Hint.TLabel',
                             font=('Segoe UI', 8),
                             foreground="#747d8c",
                             background=self.card_color)
        self.style.configure('Result.TLabel',
                             font=('Segoe UI', 16, 'bold'),
                             foreground=self.secondary_color,
                             background=self.bg_color)

        # Button styles
        self.style.configure('Primary.TButton',
                             font=('Segoe UI', 12, 'bold'),
                             foreground="white",
                             background=self.primary_color,
                             borderwidth=0,
                             padding=10)
        self.style.map('Primary.TButton',
                       background=[('active', "#0097e6"), ('!disabled', self.primary_color)])

        # Combobox styles
        self.style.configure('Modern.TCombobox',
                             fieldbackground="white",
                             foreground=self.text_color,
                             background="white",
                             selectbackground=self.highlight_color,
                             selectforeground=self.text_color,
                             arrowsize=14,
                             arrowcolor=self.primary_color)
        self.style.map('Modern.TCombobox',
                       fieldbackground=[('readonly', 'white')],
                       selectbackground=[('readonly', self.highlight_color)])

        # Radiobutton styles
        self.style.configure('TRadiobutton',
                             background=self.card_color,
                             foreground=self.text_color,
                             font=('Segoe UI', 10))

        # Scale (Slider) styles
        self.style.configure('Horizontal.TScale',
                             background=self.card_color,
                             troughcolor=self.highlight_color,
                             sliderthickness=15)

    def create_main_container(self):
        """Crea el contenedor principal"""
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill='both', expand=True, padx=20, pady=20)

    def create_header(self):
        """Crea el encabezado"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill='x', pady=(0, 20))

        title_frame = ttk.Frame(header_frame)
        title_frame.pack(fill='both', expand=True)

        title = ttk.Label(title_frame, text="VISOR-PMML", style='Title.TLabel')
        title.pack(anchor='w')

        subtitle = ttk.Label(title_frame,
                             text="Sistema de predicción con selección controlada",
                             style='Subtitle.TLabel')
        subtitle.pack(anchor='w')

    def create_load_section(self):
        """Crea la sección para cargar el modelo"""
        load_card = ttk.Frame(self.main_container, style='Card.TFrame')
        load_card.pack(fill='x', pady=(0, 20), ipady=10, ipadx=10)

        load_frame = ttk.Frame(load_card)
        load_frame.pack(fill='x', padx=15, pady=15)

        self.load_btn = ttk.Button(load_frame,
                                   text="📂 CARGAR MODELO PMML",
                                   style='Primary.TButton',
                                   command=self.load_pmml)
        self.load_btn.pack(fill='x', ipady=5)

    def create_fields_container(self):
        """Crea el contenedor para los campos de entrada con scroll"""
        fields_card = ttk.Frame(self.main_container, style='Card.TFrame')
        fields_card.pack(fill='both', expand=True, pady=(0, 20), ipady=10, ipadx=10)

        # Canvas y scrollbar
        self.canvas = tk.Canvas(fields_card, bg=self.card_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(fields_card, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        self.scrollbar.pack(side="right", fill="y", padx=(0, 2), pady=2)

        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    def create_result_section(self):
        """Crea la sección para mostrar resultados"""
        result_card = ttk.Frame(self.main_container, style='Card.TFrame')
        result_card.pack(fill='x', pady=(0, 10), ipady=10, ipadx=10)

        self.predict_btn = ttk.Button(result_card,
                                      text="🔮 ANALIZAR Y PREDECIR",
                                      style='Primary.TButton',
                                      command=self.predict,
                                      state='disabled')
        self.predict_btn.pack(fill='x', padx=15, pady=(0, 15), ipady=5)

        self.result_label = ttk.Label(result_card,
                                      text="Carga un modelo para comenzar...",
                                      style='Result.TLabel',
                                      anchor='center')
        self.result_label.pack(fill='x', padx=10, pady=10)

    def create_footer(self):
        """Crea el pie de página"""
        footer_frame = ttk.Frame(self.main_container)
        footer_frame.pack(fill='x', pady=(10, 0))

        version = ttk.Label(footer_frame,
                            text="VISOR PMML © 2025 - Todos los derechos reservados",
                            style='Subtitle.TLabel')
        version.pack(side='left', padx=10)

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
                        'leftMargin': float(iv.get('leftMargin')),
                        'rightMargin': float(iv.get('rightMargin')),
                        'closure': iv.get('closure'),
                        'valid_values': self.generate_valid_values(float(iv.get('leftMargin')),
                                                                   float(iv.get('rightMargin')),
                                                                   iv.get('closure'))
                    }

                self.fields_info[name] = info

            self.build_input_fields()
            self.result_label.config(text="✅ Modelo cargado correctamente. ¡Listo para analizar!")
            self.predict_btn.config(state='normal')
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el modelo:\n{e}")

    def generate_valid_values(self, left, right, closure):
        """Genera valores válidos basados en el intervalo del PMML"""
        step = self.determine_step(left, right)
        values = []
        current = left

        # Ajustamos según el tipo de intervalo
        if closure in ['openOpen', 'openClosed']:
            current += step
        if closure in ['closedOpen', 'openOpen']:
            right -= step

        while current <= right:
            values.append(round(current, 4))  # Redondeamos a 4 decimales
            current += step

        return values

    def determine_step(self, left, right):
        """Determina el paso adecuado según el rango"""
        range_size = right - left
        if range_size <= 1:
            return 0.1
        elif range_size <= 10:
            return 0.5
        elif range_size <= 100:
            return 1
        else:
            return 10

    def build_input_fields(self):
        # Limpiar viejos widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.widgets.clear()

        for field, info in self.fields_info.items():
            field_frame = ttk.Frame(self.scrollable_frame, style='Card.TFrame')
            field_frame.pack(fill='x', pady=8, padx=5, ipady=8, ipadx=5)

            label = ttk.Label(field_frame, text=field.upper() + ":", style='Field.TLabel')
            label.pack(anchor='w', padx=5, pady=(5, 0))

            if info['optype'] == 'categorical' and 'values' in info:
                if len(info['values']) <= 4:  # Pocas opciones -> RadioButtons
                    self.create_radio_buttons(field_frame, field, info['values'])
                else:  # Muchas opciones -> Combobox
                    self.create_combobox(field_frame, field, info['values'])

                hint = "Opciones válidas: " + ", ".join(info['values'])
                hint_label = ttk.Label(field_frame, text=hint, style='Hint.TLabel')
                hint_label.pack(anchor='w', padx=5, pady=(0, 5))

            elif info['optype'] == 'continuous' and 'interval' in info:
                if 'valid_values' in info['interval'] and len(info['interval']['valid_values']) <= 20:
                    # Si hay pocos valores posibles, usamos combobox
                    self.create_combobox(field_frame, field, info['interval']['valid_values'])
                else:
                    # Para muchos valores o rangos continuos, usamos slider con pasos discretos
                    self.create_slider(field_frame, field, info['interval'])

                iv = info['interval']
                hint = f"Rango válido: {iv['leftMargin']} a {iv['rightMargin']} ({iv['closure']})"
                hint_label = ttk.Label(field_frame, text=hint, style='Hint.TLabel')
                hint_label.pack(anchor='w', padx=5, pady=(0, 5))

            else:  # Campo genérico (deberíamos evitar esto)
                self.create_combobox(field_frame, field, [])
                hint_label = ttk.Label(field_frame, text="Ingrese el valor requerido", style='Hint.TLabel')
                hint_label.pack(anchor='w', padx=5, pady=(0, 5))

    def create_combobox(self, parent, field, values):
        """Crea un combobox para selección"""
        combo = ttk.Combobox(parent,
                             values=values,
                             state='readonly',
                             style='Modern.TCombobox',
                             font=('Segoe UI', 10))
        if values:
            combo.current(0)
        combo.pack(fill='x', padx=5, pady=2)
        self.widgets[field] = combo

    def create_radio_buttons(self, parent, field, values):
        """Crea radio buttons para pocas opciones"""
        rb_frame = ttk.Frame(parent)
        rb_frame.pack(fill='x', padx=5, pady=2)

        selected_value = tk.StringVar(value=values[0])

        for i, value in enumerate(values):
            rb = ttk.Radiobutton(rb_frame,
                                 text=value,
                                 value=value,
                                 variable=selected_value,
                                 style='TRadiobutton')
            rb.pack(side='left', padx=(0, 10))

        self.widgets[field] = selected_value

    def create_slider(self, parent, field, interval):
        """Crea un slider para valores continuos con pasos discretos"""
        slider_frame = ttk.Frame(parent)
        slider_frame.pack(fill='x', padx=5, pady=2)

        min_val = interval['leftMargin']
        max_val = interval['rightMargin']

        # Usamos valores válidos si existen, o generamos pasos discretos
        if 'valid_values' in interval and interval['valid_values']:
            values = interval['valid_values']
            min_val = min(values)
            max_val = max(values)
            step = (max_val - min_val) / (len(values) - 1) if len(values) > 1 else 1
        else:
            step = self.determine_step(min_val, max_val)
            values = []
            current = min_val
            while current <= max_val:
                values.append(current)
                current += step

        current_val = values[0]

        slider_var = tk.DoubleVar(value=current_val)
        slider = ttk.Scale(slider_frame,
                           from_=min_val,
                           to=max_val,
                           variable=slider_var,
                           style='Horizontal.TScale')
        slider.pack(fill='x', expand=True)

        value_label = ttk.Label(slider_frame,
                                text=f"{current_val:.4f}",
                                style='Field.TLabel')
        value_label.pack(side='right', padx=5)

        # Función para encontrar el valor más cercano en la lista de valores válidos
        def get_closest_value(val):
            float_val = float(val)
            closest = min(values, key=lambda x: abs(float(x) - float_val))
            return closest

        # Actualizar label cuando se mueve el slider
        def update_label(val):
            if not self.updating_slider:
                self.updating_slider = True
                try:
                    closest_val = get_closest_value(val)
                    value_label.config(text=f"{float(closest_val):.4f}")
                    slider_var.set(closest_val)  # Ajusta a valor válido
                finally:
                    self.updating_slider = False

        slider.configure(command=lambda v: update_label(v))

        # Asegurar que el valor inicial es válido
        slider_var.set(current_val)

        self.widgets[field] = slider_var

    def predict(self):
        if not self.model:
            messagebox.showwarning("Modelo no cargado", "Primero carga un modelo PMML.")
            return

        try:
            data = {}
            for field, widget in self.widgets.items():
                if isinstance(widget, tk.StringVar):  # RadioButton
                    val = widget.get()
                elif isinstance(widget, tk.DoubleVar):  # Slider
                    val = widget.get()
                else:  # Combobox
                    val = widget.get()

                if not val:
                    raise ValueError(f"Debe seleccionar un valor para '{field}'")

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

            self.result_label.config(text=f"🔍 RESULTADO: {pred}", foreground=self.secondary_color)

        except Exception as e:
            messagebox.showerror("Error en predicción", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = PMMLApp(root)
    root.mainloop()