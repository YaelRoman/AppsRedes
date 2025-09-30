from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Alumno(Base):
    __tablename__ = 'alumnos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    edad = Column(Integer)

engine = create_engine('sqlite:///Practica11/escuelita2.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def agregar_alumno(nombre, edad):
    alumno = Alumno(nombre=nombre, edad=edad)
    session.add(alumno)
    session.commit()
    print(f'Alumno agregado: {alumno.nombre}, {alumno.edad}')

def mostrar_alumnos():
    alumnos = session.query(Alumno).all()
    for alumno in alumnos:
        print(f'ID: {alumno.id}, Nombre: {alumno.nombre}, Edad: {alumno.edad}')

def actualizar_alumno(id, nuevo_nombre, nueva_edad):
    alumno = session.query(Alumno).filter_by(id=id).first()
    if alumno:
        alumno.nombre = nuevo_nombre
        alumno.edad = nueva_edad
        session.commit()
        print(f'Alumno actualizado: {alumno.nombre}, {alumno.edad}')
    else:
        print('Alumno no encontrado.')

def borrar_alumno(id):
    alumno = session.query(Alumno).filter_by(id=id).first()
    if alumno:
        session.delete(alumno)
        session.commit()
        print('Alumno borrado.')
    else:
        print('Alumno no encontrado.')

while True:
    print("\n1. Agregar alumno\n2. Mostrar alumnos\n3. Actualizar alumno\n4. Borrar alumno\n5. Salir")
    opcion = input("Elige una opción: ")
    if opcion == '1':
        nombre = input("Nombre: ")
        edad = int(input("Edad: "))
        agregar_alumno(nombre, edad)
    elif opcion == '2':
        mostrar_alumnos()
    elif opcion == '3':
        id = int(input("ID del alumno a actualizar: "))
        nombre = input("Nuevo nombre: ")
        edad = int(input("Nueva edad: "))
        actualizar_alumno(id, nombre, edad)
    elif opcion == '4':
        id = int(input("ID del alumno a borrar: "))
        borrar_alumno(id)
    elif opcion == '5':
        break
    else:
        print("Opción inválida.")