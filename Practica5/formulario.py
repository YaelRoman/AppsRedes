import tkinter as tk
from tkinter import messagebox
import re

def validar_entradas():
    nombre = var_nombre.get()
    apellido_paterno = var_apellido_paterno.get()
    apellido_materno = var_apellido_materno.get()
    fecha_nacimiento = var_fecha_nacimiento.get()
    sexo = var_sexo.get()

    # Expresiones regulares
    regex_nombre = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$"
    regex_fecha = r"^\d{2}/\d{2}/\d{4}$"
    regex_sexo = r"^(Masculino|Femenino)$"

    errores = []
    if not re.match(regex_nombre, nombre):
        errores.append("Nombre inválido.")
    if not re.match(regex_nombre, apellido_paterno):
        errores.append("Apellido paterno inválido.")
    if not re.match(regex_nombre, apellido_materno):
        errores.append("Apellido materno inválido.")
    if not re.match(regex_fecha, fecha_nacimiento):
        errores.append("Fecha de nacimiento inválida. Formato: dd/mm/aaaa")
    if not re.match(regex_sexo, sexo):
        errores.append("Sexo inválido. Seleccione Masculino o Femenino.")

    if errores:
        messagebox.showerror("Error de validación", "\n".join(errores))
    else:
        guardar_datos(nombre, apellido_paterno, apellido_materno, fecha_nacimiento, sexo)
        messagebox.showinfo("Éxito", "Datos guardados correctamente.")
        limpiar_campos()

def guardar_datos(nombre, apellido_paterno, apellido_materno, fecha_nacimiento, sexo):
    with open("datos_formulario.txt", "a", encoding="utf-8") as f:
        f.write(f"{nombre},{apellido_paterno},{apellido_materno},{fecha_nacimiento},{sexo}\n")

def limpiar_campos():
    var_nombre.set("")
    var_apellido_paterno.set("")
    var_apellido_materno.set("")
    var_fecha_nacimiento.set("")
    var_sexo.set("")

root = tk.Tk()
root.title("Formulario Básico")

# Variables
var_nombre = tk.StringVar()
var_apellido_paterno = tk.StringVar()
var_apellido_materno = tk.StringVar()
var_fecha_nacimiento = tk.StringVar()
var_sexo = tk.StringVar()

# Etiquetas y entradas
tk.Label(root, text="Nombre:").grid(row=0, column=0, sticky="e")
tk.Entry(root, textvariable=var_nombre).grid(row=0, column=1)

tk.Label(root, text="Apellido Paterno:").grid(row=1, column=0, sticky="e")
tk.Entry(root, textvariable=var_apellido_paterno).grid(row=1, column=1)

tk.Label(root, text="Apellido Materno:").grid(row=2, column=0, sticky="e")
tk.Entry(root, textvariable=var_apellido_materno).grid(row=2, column=1)

tk.Label(root, text="Fecha de Nacimiento (dd/mm/aaaa):").grid(row=3, column=0, sticky="e")
tk.Entry(root, textvariable=var_fecha_nacimiento).grid(row=3, column=1)

tk.Label(root, text="Sexo:").grid(row=4, column=0, sticky="e")
sexo_opciones = ["Masculino", "Femenino"]
tk.OptionMenu(root, var_sexo, *sexo_opciones).grid(row=4, column=1)

tk.Button(root, text="Guardar", command=validar_entradas).grid(row=5, column=0, columnspan=2, pady=10)

root.mainloop()