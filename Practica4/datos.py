import os
import re

dirPath = os.path.dirname(os.path.abspath(__file__))
archivo = os.path.join(dirPath, 'archivo.txt')
exCorreo = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
exTelefono = r"(?:\+52\s?)?(?:\(?\d{2,3}\)?[\s-]?)?\d{4}[\s-]?\d{4}"

try:
    with open(archivo, 'r') as a:
        texto = a.read()
        print(texto)
        correos = re.findall(exCorreo, texto)
        telefonos = re.findall(exTelefono, texto)

        print('\nCorreos:')
        for correo in correos:
            print(correo)
        print('\nTelefonos:')     
        for telefono in telefonos:
            print(telefono)
    a.close()
except FileNotFoundError:
    print('No se encontró el archivo')
except Exception as e:
    print('Error', e)

