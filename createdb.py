import csv
import sqlite3 as sql

def readcsv():
    #Checks if the file already exists
    try:
        clients = []

        #Open the file and append the names to the list
        with open("clients.csv") as file:
            reader = csv.reader(file, delimiter = ";")
            #Skips the header
            next(file)
            for i in reader:
                clients.append(tuple(i))
        print("File sucessfully read")

        return clients

    except:
        print("Unexisting file")

def createdb():
    conn = sql.connect("clients.db")
    cursor = conn.cursor()

    #If the table already exists, it will show an error message
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
        print("Table sucesfully created")
    
    except:
        print("Existing table, no changes were made")

    cursor.executemany("INSERT INTO clients VALUES (null,?,?,?,?,?)", readcsv())
    conn.commit()
    conn.close()

createdb()
