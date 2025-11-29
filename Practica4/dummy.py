import re

parrafo = '''
Esta es una cadena de varias
lineas con comillas
triples'''

print(parrafo)

print(parrafo.find('cadena'))

frutas = 'pera,manzana,uva,fresa'
for fruta in frutas.split(','):
    print("\"", fruta.capitalize(), '"')

frase = 'Te quiero mucho Alessio'
print(frase.replace('Alessio','Yael'))

frase = 'Me gusta mucho la {}'

for fruta in frutas.split(','):
    print(frase.format(fruta))

frase = 'Me llamo {} y tengo {}'
print(frase.format('Andres','23'))

a = 'Hola cómo estás?'
b = '073457'

print (re.findall('[0-9]', a),re.findall('[0-9]', b)) 

telefono = '5534261755 '
print(re.findall(r'^\d{10}$', telefono))

# Regex contraseña 1 caracter especial, mayusculas, minusculas 
# y 8 caracteres
patitoPass = 'patito123'
regex = '^(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9]).{8,}$'
print(re.findall(regex, patitoPass))

patitoAdvancedPass = 'Patito123$'
print(re.findall(regex, patitoAdvancedPass))

archivo = open('frutas.txt','w')
archivo.write(frutas)
archivo.close()

archivo = open('frutas.txt', 'r')
contenido = archivo.read()
archivo.close()

print(contenido)

try: 
    direcciones = open('direcciones.txt', 'r')
    print('Archivo abierto correctamente')
except:
    print('Error abriendo archivo')