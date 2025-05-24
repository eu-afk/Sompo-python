import pymysql
import traceback

def criar_banco_e_tabelas():
    try:
        # Conexão inicial sem banco selecionado
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="Root!1126",  # coloque sua senha aqui se tiver
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()

        # Cria o banco se não existir
        cursor.execute("CREATE DATABASE IF NOT EXISTS usuario_seguradora")
        cursor.execute("USE usuario_seguradora")

        # Criação das tabelas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            cpf VARCHAR(11) UNIQUE NOT NULL,
            nascimento DATE,
            endereco VARCHAR(255),
            telefone VARCHAR(20),
            email VARCHAR(100)
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS apolices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            numero VARCHAR(20) UNIQUE NOT NULL,
            cliente_id INT NOT NULL,
            tipo_seguro VARCHAR(50) NOT NULL,
            dados_seguro TEXT,
            valor_segurado DECIMAL(10,2) NOT NULL,
            valor_mensal DECIMAL(10,2) NOT NULL,
            vigencia VARCHAR(50),
            data_emissao DATE,
            status VARCHAR(20) DEFAULT 'Ativa',
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sinistros (
            id INT AUTO_INCREMENT PRIMARY KEY,
            apolice_numero VARCHAR(20) NOT NULL,
            descricao TEXT,
            data_ocorrencia DATE,
            status VARCHAR(20) DEFAULT 'Aberto',
            FOREIGN KEY (apolice_numero) REFERENCES apolices(numero) ON DELETE CASCADE
        )""")

        print("Banco de dados e tabelas criados com sucesso.")
    except Exception as e:
        traceback.print_exc()
        print("Erro ao criar banco de dados ou tabelas:", e)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    criar_banco_e_tabelas()
