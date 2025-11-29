# Programa que cifra/descifra un mensaje mediante la cifra César
import pyperclip

alfabeto = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
salida = ''

modo = input('Ingresa la operación a realizar Cifrar(c)/Descifrar(d): ')

texto = input('Ingresa el texto: ')
clave = int(input('Ingresa la clave (1-25): '))

for simbolo in texto.upper():
    if simbolo in alfabeto:
        pos = alfabeto.find(simbolo)
        if modo == 'c': pos += clave
        elif modo == 'd': pos -= clave
        pos %= 26

        salida += alfabeto[pos]
    else:
        salida += simbolo

print(salida)
pyperclip.copy(salida)