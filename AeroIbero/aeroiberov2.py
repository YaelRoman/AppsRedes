from tkinter import *
# guardar
def guardarDatos():
    nombre = nombre_entry.get() # se obtienen los datos de los entries
    apellidoP = apellidoP_entry.get()
    apellidoM = apellidoM_entry.get()
    fechaN = fechaN_entry.get()
    raza = raza_entry.get()
    correo = correo_entry.get()
    telefono = telefono_entry.get()
    extras = extras_entry.get()
    print('\n\nDatos Usuario:'+nombre+' '+apellidoP+' '+apellidoM+' '+fechaN+' '+raza+' '+correo+' '+telefono+' '+extras+'\n\n') # print de control
    # aquí va la magia de guardar datos en un archivo maybe ?
    
def checarRutas():
    origen = origen_entry.get()
    destino = destino_entry.get()
    print(f'\n\nDatos Ruta: {origen} {destino}\n\n') # print de control
    # aquí va la magia de dijkstra
    res1 = 'Dijkstra Precio'
    res2 = 'Dijkstra Distancia'
    res3 = 'Dijkstra Tiempo'
    reMinPrecio_label.config(text=f'{res1}')
    reMinDistancia_label.config(text=f'{res2}')
    reMinTiempo_label.config(text=f'{res3}')
    
    
# ventana
root = Tk()
root.title("Formulario de Reservación ✈️")

# frame vuelo
frame_vuelo = Frame(root, padx=10, pady=10, relief=GROOVE, borderwidth=2)
frame_vuelo.pack(padx=10, pady=10, fill="x")

datosVuelo_label = Label(frame_vuelo, text="Datos Vuelo", font=("Arial", 12, "bold"))
datosVuelo_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

origen_label = Label(frame_vuelo, text="Origen:")
origen_label.grid(row=1, column=0, sticky="e", padx=5, pady=2)
origen_entry = Entry(frame_vuelo)
origen_entry.grid(row=1, column=1, padx=5, pady=2)

destino_label = Label(frame_vuelo, text="Destino:")
destino_label.grid(row=2, column=0, sticky="e", padx=5, pady=2)
destino_entry = Entry(frame_vuelo)
destino_entry.grid(row=2, column=1, padx=5, pady=2)

fecha_label = Label(frame_vuelo, text="Fecha:")
fecha_label.grid(row=3, column=0, sticky="e", padx=5, pady=2)
fecha_entry = Entry(frame_vuelo)
fecha_entry.grid(row=3, column=1, padx=5, pady=2)


# frame rutas
frame_rutas = Frame(root, padx=10, pady=10, relief=GROOVE, borderwidth=2)
frame_rutas.pack(padx=10, pady=10, fill="x")

rutas_label = Label(frame_rutas, text="Rutas", font=("Arial", 12, "bold"))
rutas_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

ruta_var = IntVar(value=0)  # guarda cuál está seleccionado

minPrecio_label = Label(frame_rutas, text="Menor Precio:")
minPrecio_label.grid(row=1, column=0, sticky="e", padx=5, pady=2)
reMinPrecio_label = Label(frame_rutas, text="Ruta de menor precio")
reMinPrecio_label.grid(row=1, column=1, padx=5, pady=2)
minPrecio_radio = Radiobutton(frame_rutas, variable=ruta_var, value=1)
minPrecio_radio.grid(row=1, column=2, padx=5)

minDistancia_label = Label(frame_rutas, text="Menor Distancia:")
minDistancia_label.grid(row=2, column=0, sticky="e", padx=5, pady=2)
reMinDistancia_label = Label(frame_rutas, text="Ruta de menor distancia")
reMinDistancia_label.grid(row=2, column=1, padx=5, pady=2)
minDistancia_radio = Radiobutton(frame_rutas, variable=ruta_var, value=2)
minDistancia_radio.grid(row=2, column=2, padx=5)

minTiempo_label = Label(frame_rutas, text="Menor Tiempo:")
minTiempo_label.grid(row=3, column=0, sticky="e", padx=5, pady=2)
reMinTiempo_label = Label(frame_rutas, text="Ruta de menor tiempo")
reMinTiempo_label.grid(row=3, column=1, padx=5, pady=2)
minTiempo_radio = Radiobutton(frame_rutas, variable=ruta_var, value=3)
minTiempo_radio.grid(row=3, column=2, padx=5)


# botón rutas
ruta_button = Button(root, text="Checar Rutas", font=("Arial", 11, "bold"), bg="#4CAF50", fg="gray", command=checarRutas)
ruta_button.pack(pady=15)


# frame usuario
frame_usuario = Frame(root, padx=10, pady=10, relief=GROOVE, borderwidth=2)
frame_usuario.pack(padx=10, pady=10, fill="x")

datosUsuario_label = Label(frame_usuario, text="Datos Usuario", font=("Arial", 12, "bold"))
datosUsuario_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

nombre_label = Label(frame_usuario, text="Nombre:")
nombre_label.grid(row=1, column=0, sticky="e", padx=5, pady=2)
nombre_entry = Entry(frame_usuario)
nombre_entry.grid(row=1, column=1, padx=5, pady=2)

apellidoP_label = Label(frame_usuario, text="Apellido Paterno:")
apellidoP_label.grid(row=2, column=0, sticky="e", padx=5, pady=2)
apellidoP_entry = Entry(frame_usuario)
apellidoP_entry.grid(row=2, column=1, padx=5, pady=2)

apellidoM_label = Label(frame_usuario, text="Apellido Materno:")
apellidoM_label.grid(row=3, column=0, sticky="e", padx=5, pady=2)
apellidoM_entry = Entry(frame_usuario)
apellidoM_entry.grid(row=3, column=1, padx=5, pady=2)

fechaN_label = Label(frame_usuario, text="Fecha de Nacimiento:")
fechaN_label.grid(row=4, column=0, sticky="e", padx=5, pady=2)
fechaN_entry = Entry(frame_usuario)
fechaN_entry.grid(row=4, column=1, padx=5, pady=2)

raza_label = Label(frame_usuario, text="Raza:")
raza_label.grid(row=5, column=0, sticky="e", padx=5, pady=2)
raza_entry = Entry(frame_usuario)
raza_entry.grid(row=5, column=1, padx=5, pady=2)

correo_label = Label(frame_usuario, text="Correo:")
correo_label.grid(row=6, column=0, sticky="e", padx=5, pady=2)
correo_entry = Entry(frame_usuario)
correo_entry.grid(row=6, column=1, padx=5, pady=2)

telefono_label = Label(frame_usuario, text="Celular:")
telefono_label.grid(row=7, column=0, sticky="e", padx=5, pady=2)
telefono_entry = Entry(frame_usuario)
telefono_entry.grid(row=7, column=1, padx=5, pady=2)

extras_label = Label(frame_usuario, text="Acompañantes:")
extras_label.grid(row=8, column=0, sticky="e", padx=5, pady=2)
extras_entry = Entry(frame_usuario)
extras_entry.grid(row=8, column=1, padx=5, pady=2)

    
# botón registro
registro_button = Button(root, text="Registro", font=("Arial", 11, "bold"), bg="#4CAF50", fg="gray", command=guardarDatos)
registro_button.pack(pady=15)

root.mainloop()