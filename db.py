import mysql.connector

def conectar():
    return mysql.connector.connect(
        host="localhost",      
        user="root",  
        password="Root!1126",  
        database="usuario_seguradora" 
    )
