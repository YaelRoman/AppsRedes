import tkinter as tk
from tkinter import ttk
from ctypes import windll

#  Arregla UI borrosa en windows
windll.shcore.SetProcessDpiAwareness(1)

root = tk.Tk()

# Cambiar el titulo
root.title('Calculadora')

# Cambia el tamaño de la ventana y centrarla
window_width = 300
window_height = 150

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

center_x = int(screen_width/2 - window_width/2)
center_y = int(screen_height/2 - window_height/2)

root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

# Bloquear cambio de tamaño
root.resizable(False,False)

# Coloca una etiqueta
message = ttk.Label(root, text = '0')
message.pack(expand=False, side='top')

num = ttk.Entry(root, text= 'Número')
num.pack()

frame = tk.Frame(root)
frame.pack()

# Coloca los botones de operaciones
btnSum = ttk.Button(frame, text = '+')
btnSum.grid(row = 0, column = 0, pady = 5)

btnSub = ttk.Button(frame, text = '-')
btnSub.grid(row = 0, column = 1, pady = 5)

btnMult = ttk.Button(frame, text = 'x')
btnMult.grid(row = 1, column = 0)

btnEq = ttk.Button(frame, text = '=')
btnEq.grid(row = 1, column = 1)



def sumClicked(event):
    resultado = eval(message.cget("text"))
    resultado += eval(num.get())
    message.config(text= str(resultado))

def subClicked():
    resultado = eval(message.cget("text"))
    resultado -= eval(num.get())
    message.config(text= str(resultado))

def multClicked():
    resultado = eval(message.cget("text"))
    resultado *= eval(num.get())
    message.config(text= str(resultado))

def eqClicked():
    resultado = eval(message.cget("text"))
    resultado = eval(num.get())
    message.config(text= str(resultado))

btnSum.bind('<ButtonPress>', sumClicked)

# Mantiene la ventana mostrandose
root.mainloop()