import os
import random

dir = os.path.dirname(os.path.abspath(__file__))
amigosPath = os.path.join(dir, 'amigos.txt')
mensaje = os.path.join(dir, 'mensaje.txt')
deseos = os.path.join(dir, 'deseos.txt')
dia = 2


try:
    with open(deseos, 'r') as d:
        deseosTxt = d.read().split('\n')
        print(deseosTxt)
    with open(amigosPath,'r') as n:
        for amigo in n.read().split('\n'):
            carta = os.path.join(dir, "Cartas",amigo + '.txt')
            with open(carta, 'w') as carta:
                with open(mensaje, 'r') as m:
                    mensajeTxt = str(m.read())
                    carta.write(mensajeTxt.format(amigo, random.choice(deseosTxt), f'{dia} de Enero'))
                    m.close() 
            carta.close()
            dia += 1
except FileNotFoundError:
    print('Error abriendo archivo')
except Exception as e:
    print('Error', e)