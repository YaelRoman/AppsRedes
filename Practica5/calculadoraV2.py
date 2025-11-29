import tkinter as tk
from tkinter import ttk
from ctypes import windll
import math

#  Arregla UI borrosa en windows
windll.shcore.SetProcessDpiAwareness(1)

root = tk.Tk()
root.configure(bg="#2b2b2b")

# Cambiar el titulo
root.title('Calculadora avanzada')

# Cambia el tamaño de la ventana y centrarla
window_width = 505
window_height = 340

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

center_x = int(screen_width/2 - window_width/2)
center_y = int(screen_height/2 - window_height/2)

root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

# Bloquear cambio de tamaño
root.resizable(False,False)

# Estilo
style = ttk.Style(root)
style.theme_use("default")
style.configure(
    "Dark.TButton",
    background="#3c3f41",
    foreground="white",
    font=("Segoe UI", 11),
    padding=10,
    relief="flat"
)
style.configure(
    "Pink.TButton",
    background="#e32c75",
    foreground="white",
    font=("Segoe UI", 11),
    padding=10,
    relief="flat"
)
style.map(
    "Pink.TButton",
    background=[("active", "#FF71BD")],
    foreground=[("disabled", "gray")]
)
style.map(
    "Dark.TButton",
    background=[("active", "#555555")],
    foreground=[("disabled", "gray")]
)
style.configure(
    "Dark.TLabel",
    background="#2b2b2b",
    foreground="white",
    font=("Segoe UI", 18),
    padding=(10, 10)
)

# Coloca una etiqueta
message = ttk.Label(root, text = '', style="Dark.TLabel")
message.pack(expand=False, side='top')

frame = tk.Frame(root, background="#2b2b2b")
frame.pack()

# Coloca los botones de operaciones
btns = [['**2'  ,'pi', 'e', 'C', 'del'],
        ['sqrt' , '(', ')', '!', '/'  ],
        ['**'   , '7', '8', '9', '*'  ],
        ['10**' , '4', '5', '6', '-'  ],
        ['log'  , '1', '2', '3', '+'  ],
        ['ln'   , '%', '0', '.', '='  ]]

def on_button_click(symbol):
    current = message.cget("text")
    if current == "Error": current = ""
    message.config(text=current + symbol)

def evaluate():
    try:
        result = eval(message.cget("text"), {"__builtins__": {}}, {
            "sqrt": math.sqrt, "log": math.log, "ln": math.log, 
            "pi": math.pi, "e": math.e, "factorial": math.factorial
        })
        message.config(text=str(result))
    except Exception:
        message.config(text="Error")

def delete():
    message.config(text="")

def deleteLast():
    current = message.cget("text")
    message.config(text=current[:-1])

def factorial():
    current = message.cget("text")
    message.config(text=current + "factorial(")

special = {
    "=": evaluate,
    "C": delete,
    "del" : deleteLast,
    "!" : factorial
}

btnsObj = [
    [ttk.Button(
        frame, 
        text=text, 
        command=(special[text] if text in special else 
                 lambda s=text: on_button_click(s)),
        style="Dark.TButton" if text != "=" else "Pink.TButton"
        ) for text in row
    ]for row in btns
]

for i in range(len(btnsObj)):
    for j in range(len(btnsObj[i])):
        btnsObj[i][j].grid(row= i, column= j, padx=2, pady=1)

# Mantiene la ventana mostrandose
root.mainloop()