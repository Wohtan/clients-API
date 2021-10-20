import csv
import sqlite3 as sql

def leercsv():
    #Verifica si existe el archivo
    try:
        clients = []

        #Abrir el CSV y añadir los elementos a la lista
        with open("clients.csv") as file:
            reader = csv.reader(file, delimiter = ";")
            #Se salta el encabezado
            next(file)
            for i in reader:
                clients.append(tuple(i))
        print("Fichero leído correctamente")

        return clients

    except:
        print("Fichero inexistente")

def creardb():
    #Crea conexión a la db y crea el cursor 
    conexion = sql.connect("clients.db")
    cursor = conexion.cursor()

    #Si ya está creada la db retornará error
    try:
        cursor.execute("""
        CREATE TABLE clients (
            id  INTEGER PRIMARY KEY AUTOINCREMENT,
            customer VARCHAR(100) UNIQUE,
            country VARCHAR(2),
            region VARCHAR(3),
            sp INTEGER UNIQUE,
            sh INTEGER
        )  
        """)
        print("Tabla creada correctamente")
    
    except:
        print("Base de datos ya creada")

    cursor.executemany("INSERT INTO clients VALUES (null,?,?,?,?,?)", leercsv())
    conexion.commit()
    conexion.close()

creardb()
