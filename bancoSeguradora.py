import pymysql

def criar_banco_e_tabelas():
    conn = pymysql.connect(host='localhost', user='root', password='Root!1126')
    cursor = conn.cursor()
    cursor.execute("create database if not exists usuario_seguradora")
    cursor.execute("use usuario_seguradora")

    cursor.execute("""
    create table if not exists clientes (
        id int auto_increment primary key,
        nome varchar(100) not null,
        cpf varchar(11) unique not null,
        nascimento date,
        endereco varchar(255),
        telefone varchar(20),
        email varchar(100)
    )
    """)


    conn.commit()
    cursor.close()
    conn.close()
