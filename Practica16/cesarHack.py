# Recupera la clave de una cifra César por fuerza bruta

alfabeto = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
criptograma = input('Ingresa el criptograma: ')

for clave in range(1,len(alfabeto)):
    salida = ''
    for simbolo in criptograma:
        if simbolo in alfabeto:
            pos = alfabeto.find(simbolo)
            pos -= clave
            pos %= len(alfabeto)
            
            salida += alfabeto[pos]
        else:
            salida += simbolo

    print(f"Clave {clave}: {salida}")