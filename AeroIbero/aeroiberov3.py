from tkinter import *
from tkinter import ttk, StringVar
import graphs
import compRoutes
import random # para fines de pruebas; hay que quitarlo al final

# --- Dark Theme Setup ---
def set_dark_theme(widget):
    import tkinter.ttk as ttk_mod
    bg = "#222"
    fg = "#eee"
    for w in widget.winfo_children():
        # Skip ttk widgets (they don't support bg/fg config)
        if isinstance(w, (ttk_mod.Entry, ttk_mod.Button, ttk_mod.Combobox, ttk_mod.Label, ttk_mod.Frame)):
            continue
        if isinstance(w, (Frame, LabelFrame)):
            w.config(bg=bg)
            set_dark_theme(w)
        elif isinstance(w, Label):
            w.config(bg=bg, fg=fg)
        elif isinstance(w, Entry):
            w.config(bg="#333", fg=fg, insertbackground=fg)
        elif isinstance(w, Button):
            w.config(bg="#444", fg=fg, activebackground="#333", activeforeground=fg)
        elif isinstance(w, Radiobutton):
            w.config(bg=bg, fg=fg, selectcolor="#444", activebackground=bg, activeforeground=fg)
        elif isinstance(w, Toplevel):
            w.config(bg=bg)
            set_dark_theme(w)
        # Add more widget types as needed

def apply_dark_theme():
    root.config(bg="#222")
    set_dark_theme(root)

    # Basic ttk dark styling so Comboboxes look consistent
    try:
        style = ttk.Style()
        # Use a theme that honors custom colors on most platforms
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure(
            "TCombobox",
            fieldbackground="#333",
            background="#333",
            foreground="#eee"
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", "#333")],
            foreground=[("readonly", "#eee")]
        )
    except Exception:
        pass


# guardar
def guardarDatos(): # función para guardar los datos del cliente que reserva
    
    registro_button.config(state="disabled")  # bloquea el botón después de usarlo
    
    # se obtienen los datos de los entries de la ventana principal
    origen = origen_var.get()
    destino = destino_var.get()
    ruta = ruta_var.get()
    nombre = nombre_entry.get()
    apellidoP = apellidoP_entry.get()
    apellidoM = apellidoM_entry.get()
    fechaN = fechaN_entry.get()
    raza = raza_entry.get()
    correo = correo_entry.get()
    telefono = telefono_entry.get()
    extras = extras_entry.get()
    
    # se abre una ventana adicional para el registro de los acompañantes
    try:
        extras_num = int(extras)
    except Exception:
        extras_num = 0
    
    if extras_num >= '1':
        registroExtras()
    
    num_id = 'id'
    tiempo = 'tiempo'
    costoVuelo = 'costo vuelo'
    cuotaAeropuerto = 'cuota aeropuerto'
    descuento = 'descuento'
    
    
    # se crea nueva ventana para desplegar los datos de la reservación
    ventana2 = Toplevel(root)
    ventana2.title(f'Registro Reservación 🎫')
    ventana2.resizable(False, False)

    frame_ventana2 = Frame(ventana2, padx=10, pady=10, relief=GROOVE, borderwidth=2)
    frame_ventana2.pack(padx=10, pady=10, fill='x')

    frame_ventana2.columnconfigure(0, weight=1)

    datosReservacion_label = Label(frame_ventana2, text='Datos Reservación', font=('Arial', 12, 'bold'))
    datosReservacion_label.grid(row=0, column=0, columnspan=1, pady=(0, 10))

    origen_label = Label(frame_ventana2, text='')
    origen_label.grid(row=1, column=0, sticky='', padx=5, pady=2)
    origen_label.config(text=f'Origen: {origen}')

    destino_label = Label(frame_ventana2, text='')
    destino_label.grid(row=2, column=0, sticky='', padx=5, pady=2)
    destino_label.config(text=f'Destino: {destino}')

    fecha_label = Label(frame_ventana2, text='')
    fecha_label.grid(row=3, column=0, sticky='', padx=5, pady=2)
    fecha_label.config(text=f'Fecha: {fechaN}')

    rutaElegida_label = Label(frame_ventana2, text='')
    rutaElegida_label.grid(row=4, column=0, sticky='', padx=5, pady=2)
    rutaElegida_label.config(text=f'Ruta: {ruta}')
    
    tiempo_label = Label(frame_ventana2, text='')
    tiempo_label.grid(row=5, column=0, sticky='', padx=5, pady=2)
    tiempo_label.config(text=f'Tiempo Estimado: {tiempo}')

    datosUsuario_label = Label(frame_ventana2, text='Datos Usuario', font=('Arial', 12, 'bold'))
    datosUsuario_label.grid(row=6, column=0, columnspan=1, pady=(0, 10))

    id_label = Label(frame_ventana2, text='')
    id_label.grid(row=7, column=0, sticky='', padx=5, pady=2)
    id_label.config(text=f'ID: {num_id}')

    nombre_label = Label(frame_ventana2, text='')
    nombre_label.grid(row=8, column=0, sticky='', padx=5, pady=2)
    nombre_label.config(text=f'Nombre: {nombre}')

    apellidoP_label = Label(frame_ventana2, text='')
    apellidoP_label.grid(row=9, column=0, sticky='', padx=5, pady=2)
    apellidoP_label.config(text=f'Apellido Paterno: {apellidoP}')

    apellidoM_label = Label(frame_ventana2, text='')
    apellidoM_label.grid(row=10, column=0, sticky='', padx=5, pady=2)
    apellidoM_label.config(text=f'Apellido Materno: {apellidoM}')

    fechaN_label = Label(frame_ventana2, text='')
    fechaN_label.grid(row=11, column=0, sticky='', padx=5, pady=2)
    fechaN_label.config(text=f'Fecha de Nacimiento: {fechaN}')

    raza_label = Label(frame_ventana2, text='')
    raza_label.grid(row=12, column=0, sticky='', padx=5, pady=2)
    raza_label.config(text=f'Raza: {raza}')

    correo_label = Label(frame_ventana2, text='')
    correo_label.grid(row=13, column=0, sticky='', padx=5, pady=2)
    correo_label.config(text=f'Correo: {correo}')

    telefono_label = Label(frame_ventana2, text='')
    telefono_label.grid(row=14, column=0, sticky='', padx=5, pady=2)
    telefono_label.config(text=f'Celular: {telefono}')

    extras_label = Label(frame_ventana2, text='')
    extras_label.grid(row=15, column=0, sticky='', padx=5, pady=2)
    extras_label.config(text=f'Acompañantes: {extras}')

    precio_label = Label(frame_ventana2, text='Datos Precio', font=('Arial', 12, 'bold'))
    precio_label.grid(row=16, column=0, columnspan=1, pady=(0, 10))

    costoVuelo_label = Label(frame_ventana2, text='')
    costoVuelo_label.grid(row=17, column=0, sticky='', padx=5, pady=2)
    costoVuelo_label.config(text=f'Costo Vuelo: {costoVuelo}')

    cuotaAeropuerto_label = Label(frame_ventana2, text='')
    cuotaAeropuerto_label.grid(row=18, column=0, sticky='', padx=5, pady=2)
    cuotaAeropuerto_label.config(text=f'Cuota Aeropuerto: {cuotaAeropuerto}')

    descuento_label = Label(frame_ventana2, text='')
    descuento_label.grid(row=19, column=0, sticky='', padx=5, pady=2)
    descuento_label.config(text=f'Descuento: {descuento}')
    
    
def registroExtras(): # función para hacer el registro de los acompañantes
    extras = int(extras_entry.get()) # la cantidad de registros a llevar a cabo

    for n in range(1, extras + 1): # se repite el formato por cada acompañante
        ventana3 = Toplevel(root)
        ventana3.title(f'Datos Acompañante {n} 🙋')
        ventana3.resizable(False, False)

        frame_ventana3 = Frame(ventana3, padx=10, pady=10, relief=GROOVE, borderwidth=2)
        frame_ventana3.pack(padx=10, pady=10, fill='x')

        frame_ventana3.columnconfigure(0, weight=1)

        datosUsuarioE_label = Label(frame_ventana3, text=f'Datos Acompañante {n}', font=('Arial', 12, 'bold'))
        datosUsuarioE_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        nombreE_label = Label(frame_ventana3, text='Nombre:')
        nombreE_label.grid(row=1, column=0, sticky='e', padx=5, pady=2)
        nombreE_entry = Entry(frame_ventana3)
        nombreE_entry.grid(row=1, column=1, padx=5, pady=2)

        apellidoPE_label = Label(frame_ventana3, text='Apellido Paterno:')
        apellidoPE_label.grid(row=2, column=0, sticky='e', padx=5, pady=2)
        apellidoPE_entry = Entry(frame_ventana3)
        apellidoPE_entry.grid(row=2, column=1, padx=5, pady=2)

        apellidoME_label = Label(frame_ventana3, text='Apellido Materno:')
        apellidoME_label.grid(row=3, column=0, sticky='e', padx=5, pady=2)
        apellidoME_entry = Entry(frame_ventana3)
        apellidoME_entry.grid(row=3, column=1, padx=5, pady=2)

        fechaNE_label = Label(frame_ventana3, text='Fecha de Nacimiento:')
        fechaNE_label.grid(row=4, column=0, sticky='e', padx=5, pady=2)
        fechaNE_entry = Entry(frame_ventana3)
        fechaNE_entry.grid(row=4, column=1, padx=5, pady=2)

        razaE_label = Label(frame_ventana3, text='Raza:')
        razaE_label.grid(row=5, column=0, sticky='e', padx=5, pady=2)
        razaE_entry = Entry(frame_ventana3)
        razaE_entry.grid(row=5, column=1, padx=5, pady=2)

        correoE_label = Label(frame_ventana3, text='Correo:')
        correoE_label.grid(row=6, column=0, sticky='e', padx=5, pady=2)
        correoE_entry = Entry(frame_ventana3)
        correoE_entry.grid(row=6, column=1, padx=5, pady=2)

        telefonoE_label = Label(frame_ventana3, text='Celular:')
        telefonoE_label.grid(row=7, column=0, sticky='e', padx=5, pady=2)
        telefonoE_entry = Entry(frame_ventana3)
        telefonoE_entry.grid(row=7, column=1, padx=5, pady=2)
        
        id_var = StringVar()
        id_var.set("ID Cliente:")
        idE_label = Label(frame_ventana3, textvariable=id_var)
        idE_label.grid(row=8, column=0, columnspan=2, padx=5, pady=2)
        
        leyenda_label = Label(frame_ventana3, text="⚠️ Debes cerrar esta ventana para continuar con el siguiente registro", fg="red", font=("Arial", 9, "italic"))
        leyenda_label.grid(row=10, column=0, columnspan=2, pady=(10, 5))
        
        def registrar():
            guardarDatosExtra(id_var) ###
            registroE_button.config(state="disabled")  # bloquea el botón después de usarlo para evitar problemas con el registro de los datos

        registroE_button = Button(ventana3, text='Registro', font=('Arial', 11, 'bold'), bg='#4CAF50', fg='gray', command=registrar)
        registroE_button.pack(pady=15)
        
        ventana3.grab_set() # hace que no se pueda interactuar con otras ventanas hasta que se cierre la ventana actual
        ventana3.wait_window() # espera a que se cierre la ventana actual antes de dejar que se cree la siguiente; mantiene orden de registro de acompañantes
        
def guardarDatosExtra(id_var,): # hay que eliminar esta función al final; solo es un placeholder
    nuevo_id = random.randint(1000,9999)
    id_var.set(f'ID Cliente: {nuevo_id}')  # actualiza el label

def rutaToLabel(ruta):
    label = ""
    numCiudades = len(ruta)
    for i in range(numCiudades-1):
        label = f"{label}{ruta[i]} - {ruta[i+1]}\n"
    return label

def horasToHorasMinutos(horas_dec):
    horas = int(horas_dec)
    minutos = int(round((horas_dec - horas) * 60))
    return horas, minutos

def checarRutas(origen: str, destino: str):
    if destino != 'Selecciona destino' and origen != 'Selecciona origen' and origen != "" and destino != "":
        print(origen, destino)
        [(rutaCosto, costo),
        (rutaDistancia, distancia),
        (rutaTiempo, tiempo)       ] = compRoutes.bestRoutes(origen, destino)
        
        #Precio
        resCosto = rutaToLabel(rutaCosto)
        resCosto = f"{resCosto}\nTotal: ${costo}\n"
        # Distancia
        resDistancia = rutaToLabel(rutaDistancia)
        resDistancia = f"{resDistancia}\nTotal: {distancia} km\n"

        #Tiempo
        resTiempo = rutaToLabel(rutaTiempo)
        horas, minutos = horasToHorasMinutos(tiempo)
        resTiempo = f"{resTiempo}\nTotal: {horas} h {minutos} m\n"
    else:
        resCosto = resDistancia = resTiempo = '-'
    
    # actualiza los labels según las rutas encontradas
    reMinPrecio_label.config(text=f'{resCosto}')
    reMinDistancia_label.config(text=f'{resDistancia}')
    reMinTiempo_label.config(text=f'{resTiempo}')
    

# ventana principal
root = Tk()
root.resizable(False, False)
root.title('Formulario de Reservación ✈️')

def on_origen_destino_change(*args):
    checarRutas(origen_var.get(), destino_var.get())

# frame vuelo
frame_vuelo = Frame(root, padx=10, pady=10, relief=GROOVE, borderwidth=2)
frame_vuelo.pack(padx=10, pady=10, fill='x')

datosVuelo_label = Label(frame_vuelo, text='Datos Vuelo', font=('Arial', 12, 'bold'))
datosVuelo_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

# Let column 1 stretch so the dropdowns expand
frame_vuelo.grid_columnconfigure(1, weight=1)

# ---- Source list for the dropdowns ----
# If your graphs module exposes a nodes list or getter, use it:
city_list = getattr(graphs, "nodes", [])
if not city_list and hasattr(graphs, "get_nodes"):
    try:
        city_list = graphs.get_nodes()
    except Exception:
        city_list = []
# Fallback (replace with your real list if needed)
# city_list = ["Aeropuerto", "Santa Fe", "Polanco", "Condesa"]

# Origen
origen_label = Label(frame_vuelo, text='Origen:')
origen_label.grid(row=1, column=0, sticky='e', padx=5, pady=2)

origen_var = StringVar()
origen_combo = ttk.Combobox(frame_vuelo, textvariable=origen_var, values=city_list, state="readonly")
origen_combo.grid(row=1, column=1, padx=5, pady=2, sticky='we')
origen_combo.set("Selecciona origen")  # optional placeholder

# Destino
destino_label = Label(frame_vuelo, text='Destino:')
destino_label.grid(row=2, column=0, sticky='e', padx=5, pady=2)

destino_var = StringVar()
destino_combo = ttk.Combobox(frame_vuelo, textvariable=destino_var, values=city_list, state="readonly")
destino_combo.grid(row=2, column=1, padx=5, pady=2, sticky='we')
destino_combo.set("Selecciona destino")  # optional placeholder

# Fecha (unchanged)
fecha_label = Label(frame_vuelo, text='Fecha:')
fecha_label.grid(row=3, column=0, sticky='e', padx=5, pady=2)
fecha_entry = Entry(frame_vuelo)
fecha_entry.grid(row=3, column=1, padx=5, pady=2)

# Events: react when user picks in the dropdowns
def _trigger_update(*_):
    on_origen_destino_change()

origen_combo.bind("<<ComboboxSelected>>", lambda e: _trigger_update())
destino_combo.bind("<<ComboboxSelected>>", lambda e: _trigger_update())

# (Optional) keep destino list synced to avoid picking same as origen
def _on_origen_selected(e=None):
    sel = origen_var.get()
    new_vals = [c for c in city_list if c != sel]
    destino_combo["values"] = new_vals
    if destino_var.get() == sel:
        destino_var.set("")
    _trigger_update()

origen_combo.bind("<<ComboboxSelected>>", _on_origen_selected)

# Also fire when changed programmatically (optional)
origen_var.trace_add("write", lambda *_: _trigger_update())
destino_var.trace_add("write", lambda *_: _trigger_update())


# frame rutas
frame_rutas = Frame(root, padx=10, pady=10, relief=GROOVE, borderwidth=2)
frame_rutas.pack(padx=10, pady=10, fill='x', expand=True)
frame_rutas.grid_columnconfigure(0, weight=1)
frame_rutas.grid_columnconfigure(1, weight=0)

rutas_label = Label(frame_rutas, text='Rutas', font=('Arial', 12, 'bold'))
rutas_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

ruta_var = IntVar(value=0)  # guarda cuál está seleccionado

minPrecio_label = Label(frame_rutas, text='Menor Precio:')
minPrecio_label.grid(row=1, column=0, sticky='w', padx=5, pady=2)
reMinPrecio_label = Label(frame_rutas, text='-')
reMinPrecio_label.grid(row=2, column=0, sticky='w', padx=5, pady=2)
minPrecio_radio = Radiobutton(frame_rutas, variable=ruta_var, value=1)
minPrecio_radio.grid(row=1, column=1, sticky='w', padx=5)

minDistancia_label = Label(frame_rutas, text='Menor Distancia:')
minDistancia_label.grid(row=3, column=0, sticky='w', padx=5, pady=2)
reMinDistancia_label = Label(frame_rutas, text='-')
reMinDistancia_label.grid(row=4, column=0, sticky='w', padx=5, pady=2)
minDistancia_radio = Radiobutton(frame_rutas, variable=ruta_var, value=2)
minDistancia_radio.grid(row=3, column=1, sticky='w',padx=5)

minTiempo_label = Label(frame_rutas, text='Menor Tiempo:')
minTiempo_label.grid(row=5, column=0, sticky='w', padx=5, pady=2)
reMinTiempo_label = Label(frame_rutas, text='-')
reMinTiempo_label.grid(row=6, column=0, sticky='w', padx=5, pady=2)
minTiempo_radio = Radiobutton(frame_rutas, variable=ruta_var, value=3)
minTiempo_radio.grid(row=5, column=1, sticky='w',padx=5)

# frame usuario
frame_usuario = Frame(root, padx=10, pady=10, relief=GROOVE, borderwidth=2)
frame_usuario.pack(padx=10, pady=10, fill='x')

datosUsuario_label = Label(frame_usuario, text='Datos Usuario', font=('Arial', 12, 'bold'))
datosUsuario_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

nombre_label = Label(frame_usuario, text='Nombre:')
nombre_label.grid(row=1, column=0, sticky='e', padx=5, pady=2)
nombre_entry = Entry(frame_usuario)
nombre_entry.grid(row=1, column=1, padx=5, pady=2)

apellidoP_label = Label(frame_usuario, text='Apellido Paterno:')
apellidoP_label.grid(row=2, column=0, sticky='e', padx=5, pady=2)
apellidoP_entry = Entry(frame_usuario)
apellidoP_entry.grid(row=2, column=1, padx=5, pady=2)

apellidoM_label = Label(frame_usuario, text='Apellido Materno:')
apellidoM_label.grid(row=3, column=0, sticky='e', padx=5, pady=2)
apellidoM_entry = Entry(frame_usuario)
apellidoM_entry.grid(row=3, column=1, padx=5, pady=2)

fechaN_label = Label(frame_usuario, text='Fecha de Nacimiento:')
fechaN_label.grid(row=4, column=0, sticky='e', padx=5, pady=2)
fechaN_entry = Entry(frame_usuario)
fechaN_entry.grid(row=4, column=1, padx=5, pady=2)

raza_label = Label(frame_usuario, text='Raza:')
raza_label.grid(row=5, column=0, sticky='e', padx=5, pady=2)
raza_entry = Entry(frame_usuario)
raza_entry.grid(row=5, column=1, padx=5, pady=2)

correo_label = Label(frame_usuario, text='Correo:')
correo_label.grid(row=6, column=0, sticky='e', padx=5, pady=2)
correo_entry = Entry(frame_usuario)
correo_entry.grid(row=6, column=1, padx=5, pady=2)

telefono_label = Label(frame_usuario, text='Celular:')
telefono_label.grid(row=7, column=0, sticky='e', padx=5, pady=2)
telefono_entry = Entry(frame_usuario)
telefono_entry.grid(row=7, column=1, padx=5, pady=2)

extras_label = Label(frame_usuario, text='Acompañantes:')
extras_label.grid(row=8, column=0, sticky='e', padx=5, pady=2)
extras_entry = Entry(frame_usuario)
extras_entry.grid(row=8, column=1, padx=5, pady=2)

# botón registro
registro_button = Button(root, text='Registro', font=('Arial', 11, 'bold'), bg='#4CAF50', fg='gray', command=guardarDatos)
registro_button.pack(pady=15)

apply_dark_theme()

root.mainloop()