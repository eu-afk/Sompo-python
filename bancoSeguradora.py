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

    cursor.execute("""
create table if not exists apolices (
    id int auto_increment primary key,
    numero varchar(20) unique not null,
    cliente_id int not null,
    tipo_seguro varchar(50),
    dados_seguro text,
    valor_segurado decimal(10,2),
    valor_mensal decimal(10,2),
    vigencia varchar(20),
    data_emissao date,
    status varchar(20),
    foreign key (cliente_id) references clientes(id)
)
""")
    
    cursor.execute("""
create table if not exists sinistros (
    id int auto_increment primary key,
    apolice_numero varchar(20) not null,
    descricao text,
    data_ocorrencia date,
    status varchar(20),
    foreign key (apolice_numero) references apolices(numero)
)
""")

    conn.commit()
    cursor.close()
    conn.close()
