import pymysql

def criar_banco_e_tabelas():
    conn = pymysql.connect(host='localhost', user='root', password='Root!1126')
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS usuario_seguradora")
    cursor.execute("USE usuario_seguradora")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        cpf VARCHAR(11) UNIQUE NOT NULL,
        nascimento DATE,
        endereco VARCHAR(255),
        telefone VARCHAR(20),
        email VARCHAR(100)
    )
    """)

    # Outras tabelas aqui...

    conn.commit()
    cursor.close()
    conn.close()
