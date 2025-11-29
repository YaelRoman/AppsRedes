# Crear una ventana
import tkinter as tk
from tkinter import ttk
from ctypes import windll
from tkinter import PhotoImage

#  Arregla UI borrosa en windows
windll.shcore.SetProcessDpiAwareness(1)

root = tk.Tk()

# Cambiar el título
root.title('Hola a todos')
# Cambia el tamaño de la ventana y centrarla
window_width = 300
window_height = 299

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

center_x = int(screen_width/2 - window_width/2)
center_y = int(screen_height/2 - window_height/2)

root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

# Cambiar el icono de la ventana
icon = PhotoImage(file='ditto.png')
root.iconphoto(True, icon)

# Bloquear cambio de tamaño
root.resizable(False,False)

# Poner transpariencia
root.attributes('-alpha',0.8)


# Coloca una etiqueta
message = tk.Label(root, text = 'Hola mundo')
message.pack()

def button_clicked():
    print('Botón presionado')

def btn_focus(event):
    print('Botón enfocado')

def log(event):
    print(event)

tk.Button(root, text='Clásico', command= button_clicked).pack()

btn = ttk.Button(root, text='Temático')
btn.bind('<FocusIn>', btn_focus)
btn.bind('<FocusIn>', log, add='+')
btn.pack(expand=True)

ttk.Checkbutton(root, text='check').pack()
ttk.Entry(root, text='Entry').pack()
ttk.Menubutton(root, text='Label').pack()

# Mantiene la ventana mostrandose
root.mainloop()
