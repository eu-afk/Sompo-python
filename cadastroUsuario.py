# sompo.py
from datetime import datetime
import traceback
import uuid
from db import conectar
from bancoSeguradora import criar_banco_e_tabelas

def validar_cpf(cpf):
    return cpf.isdigit() and len(cpf) == 11

def input_cpf():
    while True:
        cpf = input("CPF: ").strip()
        if validar_cpf(cpf):
            return cpf
        print("CPF inválido! Deve conter exatamente 11 números.")

# Entidades
class Cliente:
    def __init__(self, nome, cpf, nascimento, endereco, telefone, email):
        self.nome = nome
        self.cpf = cpf
        self.nascimento = nascimento
        self.endereco = endereco
        self.telefone = telefone
        self.email = email

class Seguro:
    def __init__(self, tipo, dados, valor_segurado):
        self.tipo = tipo
        self.dados = dados
        self.valor_segurado = valor_segurado

class Apolice:
    def __init__(self, cliente_id, seguro, vigencia):
        self.numero = str(uuid.uuid4())[:8]
        self.cliente_id = cliente_id
        self.tipo_seguro = seguro.tipo
        self.dados_seguro = seguro.dados
        self.valor_segurado = seguro.valor_segurado
        self.valor_mensal = round(seguro.valor_segurado * 0.05, 2)
        self.vigencia = vigencia
        self.data_emissao = datetime.now().strftime('%Y-%m-%d')
        self.status = "Ativa"

class Sinistro:
    def __init__(self, apolice_numero, descricao):
        self.apolice_numero = apolice_numero
        self.descricao = descricao
        self.data_ocorrencia = datetime.now().strftime('%Y-%m-%d')
        self.status = "Aberto"

class SompoSeguradora:
    def cadastrar_cliente(self, nome, cpf, nascimento, endereco, telefone, email):
        cliente = Cliente(nome, cpf, nascimento, endereco, telefone, email)
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO clientes (nome, cpf, nascimento, endereco, telefone, email) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (cliente.nome, cliente.cpf, cliente.nascimento, cliente.endereco, cliente.telefone, cliente.email)
            )
            conn.commit()
            print(f"Cliente {cliente.nome} cadastrado com sucesso.")
        except Exception as e:
            traceback.print_exc()
            print("Erro ao cadastrar cliente:", e)
        finally:
            cursor.close()
            conn.close()

    def emitir_apolice(self, cpf, tipo, dados_seguro, valor_segurado, vigencia):
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome FROM clientes WHERE cpf = %s", (cpf,))
            cliente = cursor.fetchone()

            if not cliente:
                print("Cliente não encontrado.")
                return

            cliente_id, nome = cliente
            seguro = Seguro(tipo, dados_seguro, valor_segurado)
            apolice = Apolice(cliente_id, seguro, vigencia)

            cursor.execute(
                "INSERT INTO apolices (numero, cliente_id, tipo_seguro, dados_seguro, valor_segurado, valor_mensal, vigencia, data_emissao, status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (apolice.numero, apolice.cliente_id, apolice.tipo_seguro, apolice.dados_seguro,
                 apolice.valor_segurado, apolice.valor_mensal, apolice.vigencia, apolice.data_emissao, apolice.status)
            )
            conn.commit()
            print(f"Apólice {apolice.numero} emitida com sucesso para {nome}.")
        except Exception as e:
            traceback.print_exc()
            print("Erro ao emitir apólice:", e)
        finally:
            cursor.close()
            conn.close()

    def registrar_sinistro(self, numero_apolice, descricao):
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT numero FROM apolices WHERE numero = %s", (numero_apolice,))
            if not cursor.fetchone():
                print("Apólice não encontrada.")
                return

            sinistro = Sinistro(numero_apolice, descricao)
            cursor.execute(
                "INSERT INTO sinistros (apolice_numero, descricao, data_ocorrencia, status) "
                "VALUES (%s, %s, %s, %s)",
                (sinistro.apolice_numero, sinistro.descricao, sinistro.data_ocorrencia, sinistro.status)
            )
            conn.commit()
            print("Sinistro registrado com sucesso.")
        except Exception as e:
            traceback.print_exc()
            print("Erro ao registrar sinistro:", e)
        finally:
            cursor.close()
            conn.close()

    def relatorio_geral(self):
        try:
            conn = conectar()
            cursor = conn.cursor()
            print("\n--- RELATÓRIO GERAL SOMPO SEGUROS ---")

            cursor.execute("SELECT COUNT(*) FROM apolices WHERE status = 'Ativa'")
            print("Apólices ativas:", cursor.fetchone()[0])

            cursor.execute("SELECT COUNT(*) FROM sinistros")
            print("Total de sinistros registrados:", cursor.fetchone()[0])

            cursor.execute("SELECT SUM(valor_mensal) FROM apolices")
            total = cursor.fetchone()[0]
            print("Receita mensal estimada: R$", total if total else 0)
        except Exception as e:
            traceback.print_exc()
            print("Erro ao gerar relatório:", e)
        finally:
            cursor.close()
            conn.close()

    def sinistros_por_cliente(self, cpf):
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome FROM clientes WHERE cpf = %s", (cpf,))
            cliente = cursor.fetchone()
            if not cliente:
                print("Cliente não encontrado.")
                return

            cliente_id, nome = cliente
            cursor.execute("""
                SELECT s.descricao, s.data_ocorrencia, s.status, a.numero
                FROM sinistros s
                JOIN apolices a ON s.apolice_numero = a.numero
                WHERE a.cliente_id = %s
            """, (cliente_id,))
            sinistros = cursor.fetchall()

            print(f"\nSinistros vinculados ao cliente {nome}:")
            for s in sinistros:
                print(f"- Apólice {s[3]} | {s[0]} | {s[1]} | Status: {s[2]}")
        except Exception as e:
            traceback.print_exc()
            print("Erro ao listar sinistros:", e)
        finally:
            cursor.close()
            conn.close()

def menu():
    sompo = SompoSeguradora()
    while True:
        print("\n------ SOMPO SEGUROS - MENU ------")
        print("1. Cadastrar novo cliente")
        print("2. Emitir nova apólice")
        print("3. Registrar sinistro")
        print("4. Visualizar relatório geral")
        print("5. Consultar sinistros por CPF")
        print("0. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            nome = input("Nome completo: ")
            cpf = input_cpf()
            nascimento = input("Data de nascimento (AAAA-MM-DD): ")
            endereco = input("Endereço completo: ")
            telefone = input("Telefone: ")
            email = input("Email: ")
            sompo.cadastrar_cliente(nome, cpf, nascimento, endereco, telefone, email)

        elif opcao == "2":
            cpf = input_cpf()
            print("Tipos de seguro disponíveis: Automóvel, Residencial, Vida, Empresarial, Agrícola, Transportes")
            tipo = input("Tipo de seguro: ")
            dados = input("Informações adicionais (modelo do carro, endereço, cultura, etc): ")
            valor = float(input("Valor segurado (R$): "))
            vigencia = input("Vigência (ex: 12 meses): ")
            sompo.emitir_apolice(cpf, tipo, dados, valor, vigencia)

        elif opcao == "3":
            numero_apolice = input("Número da apólice: ")
            descricao = input("Descrição do sinistro: ")
            sompo.registrar_sinistro(numero_apolice, descricao)

        elif opcao == "4":
            sompo.relatorio_geral()

        elif opcao == "5":
            cpf = input_cpf()
            sompo.sinistros_por_cliente(cpf)

        elif opcao == "0":
            print("Encerrando sistema Sompo Seguros.")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    criar_banco_e_tabelas()
    menu()