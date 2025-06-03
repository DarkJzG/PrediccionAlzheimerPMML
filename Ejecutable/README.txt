
VISOR-PMML: Sistema de Predicción
==================================

Este software es una interfaz gráfica desarrollada en Python con Tkinter que permite cargar modelos PMML (Predictive Model Markup Language) y realizar predicciones a partir de entradas definidas en dicho modelo.

Requisitos
----------
Antes de ejecutar la aplicación, asegúrate de tener instaladas las siguientes dependencias de Python:

- tkinter
- pandas
- pypmml
- pillow

Puedes instalar todas las dependencias con el siguiente comando:

    pip install pandas pypmml pillow

Uso
---
1. Ejecuta el archivo principal del programa:

       python visor_pmml.py

2. Haz clic en el botón **"📂 CARGAR MODELO PMML"** para seleccionar un archivo `.pmml` válido.
3. El sistema detectará automáticamente los campos requeridos y mostrará los controles necesarios.
4. Ingresa los valores correspondientes para cada campo.
5. Haz clic en **"🔮 ANALIZAR Y PREDECIR"** para obtener el resultado del modelo cargado.

Estructura
----------
- Interfaz construida con Tkinter y estilos personalizados.
- Soporte para campos continuos y categóricos con intervalos y valores definidos.
- Visualización moderna con scroll integrado para entrada de múltiples campos.

Créditos
--------
VISOR-PMML © 2025 - Todos los derechos reservados.
Desarrollado por [Luis Pupiales - Johan Burbano - Anthony Paguay].
Universidad Politécnica Estatal del Carchi - Tulcán

Licencia
--------
Este software es de libre uso
