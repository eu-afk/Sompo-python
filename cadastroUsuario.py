import os
import csv
from datetime import datetime
import traceback
import uuid
from db import conectar
from bancoSeguradora import criar_banco_e_tabelas

def validar_cpf(cpf):
    return cpf.isdigit() and len(cpf) == 11

def input_cpf():
    while True:
        cpf = input("cpf: ").strip()
        if validar_cpf(cpf):
            return cpf
        print("cpf inválido! deve conter exatamente 11 números.")

class cliente:
    def __init__(self, nome, cpf, nascimento, endereco, telefone, email):
        self.nome = nome
        self.cpf = cpf
        self.nascimento = nascimento
        self.endereco = endereco
        self.telefone = telefone
        self.email = email

class seguro:
    def __init__(self, tipo, dados, valor_segurado):
        self.tipo = tipo
        self.dados = dados
        self.valor_segurado = valor_segurado

class apolice:
    def __init__(self, cliente_id, seguro, vigencia):
        self.numero = str(uuid.uuid4())[:8]
        self.cliente_id = cliente_id
        self.tipo_seguro = seguro.tipo
        self.dados_seguro = seguro.dados
        self.valor_segurado = seguro.valor_segurado
        self.valor_mensal = round(seguro.valor_segurado * 0.05, 2)
        self.vigencia = vigencia
        self.data_emissao = datetime.now().strftime('%Y-%m-%d')
        self.status = "ativa"

class sinistro:
    def __init__(self, apolice_numero, descricao):
        self.apolice_numero = apolice_numero
        self.descricao = descricao
        self.data_ocorrencia = datetime.now().strftime('%Y-%m-%d')
        self.status = "aberto"

class sompo_seguradora:

    def cadastrar_cliente(self, nome, cpf, nascimento, endereco, telefone, email):
        cliente_novo = cliente(nome, cpf, nascimento, endereco, telefone, email)
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute(
                "insert into clientes (nome, cpf, nascimento, endereco, telefone, email) values (%s, %s, %s, %s, %s, %s)",
                (cliente_novo.nome, cliente_novo.cpf, cliente_novo.nascimento, cliente_novo.endereco, cliente_novo.telefone, cliente_novo.email)
            )
            conn.commit()
            print(f"cliente {cliente_novo.nome} cadastrado com sucesso.")
        except Exception as e:
            traceback.print_exc()
            print("erro ao cadastrar cliente:", e)
        finally:
            cursor.close()
            conn.close()

    def emitir_apolice(self, cpf, tipo, dados_seguro, valor_segurado, vigencia):
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("select id, nome from clientes where cpf = %s", (cpf,))
            cliente_bd = cursor.fetchone()

            if not cliente_bd:
                print("cliente não encontrado.")
                return

            cliente_id, nome = cliente_bd
            seguro_novo = seguro(tipo, dados_seguro, valor_segurado)
            apolice_nova = apolice(cliente_id, seguro_novo, vigencia)

            cursor.execute(
                "insert into apolices (numero, cliente_id, tipo_seguro, dados_seguro, valor_segurado, valor_mensal, vigencia, data_emissao, status) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (apolice_nova.numero, apolice_nova.cliente_id, apolice_nova.tipo_seguro, apolice_nova.dados_seguro,
                 apolice_nova.valor_segurado, apolice_nova.valor_mensal, apolice_nova.vigencia, apolice_nova.data_emissao, apolice_nova.status)
            )
            conn.commit()
            print(f"apólice {apolice_nova.numero} emitida com sucesso para {nome}.")
        except Exception as e:
            traceback.print_exc()
            print("erro ao emitir apólice:", e)
        finally:
            cursor.close()
            conn.close()

    def registrar_sinistro(self, numero_apolice, descricao):
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("select numero from apolices where numero = %s", (numero_apolice,))
            if not cursor.fetchone():
                print("apólice não encontrada.")
                return

            sinistro_novo = sinistro(numero_apolice, descricao)
            cursor.execute(
                "insert into sinistros (apolice_numero, descricao, data_ocorrencia, status) values (%s, %s, %s, %s)",
                (sinistro_novo.apolice_numero, sinistro_novo.descricao, sinistro_novo.data_ocorrencia, sinistro_novo.status)
            )
            conn.commit()
            print("sinistro registrado com sucesso.")
        except Exception as e:
            traceback.print_exc()
            print("erro ao registrar sinistro:", e)
        finally:
            cursor.close()
            conn.close()

    def relatorio_geral(self):
        try:
            conn = conectar()
            cursor = conn.cursor()
            print("\n--- relatório geral sompo seguros ---")

            cursor.execute("select count(*) from apolices where status = 'ativa'")
            print("apólices ativas:", cursor.fetchone()[0])

            cursor.execute("select count(*) from sinistros")
            print("total de sinistros registrados:", cursor.fetchone()[0])

            cursor.execute("select sum(valor_mensal) from apolices")
            total = cursor.fetchone()[0]
            print("receita mensal estimada: r$", total if total else 0)
        except Exception as e:
            traceback.print_exc()
            print("erro ao gerar relatório:", e)
        finally:
            cursor.close()
            conn.close()

    def sinistros_por_cliente(self, cpf):
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("select id, nome from clientes where cpf = %s", (cpf,))
            cliente_bd = cursor.fetchone()
            if not cliente_bd:
                print("cliente não encontrado.")
                return

            cliente_id, nome = cliente_bd
            cursor.execute("""
                select s.descricao, s.data_ocorrencia, s.status, a.numero
                from sinistros s
                join apolices a on s.apolice_numero = a.numero
                where a.cliente_id = %s
            """, (cliente_id,))
            sinistros = cursor.fetchall()

            print(f"\nsinistros vinculados ao cliente {nome}:")
            for s in sinistros:
                print(f"- apólice {s[3]} | {s[0]} | {s[1]} | status: {s[2]}")
        except Exception as e:
            traceback.print_exc()
            print("erro ao listar sinistros:", e)
        finally:
            cursor.close()
            conn.close()

    def exportar_clientes_csv(self, nome_arquivo='clientes_sompo.csv'):
        try:
            os.makedirs('csv', exist_ok=True)
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, cpf, nascimento, endereco, telefone, email FROM clientes")
            clientes = cursor.fetchall()

            caminho = os.path.join('csv', nome_arquivo)
            with open(caminho, mode='w', newline='', encoding='utf-8') as arquivo_csv:
                escritor = csv.writer(arquivo_csv)
                escritor.writerow(['ID', 'Nome Completo', 'CPF', 'Nascimento', 'Endereço', 'Telefone', 'E-mail'])
                for c in clientes:
                    nascimento_formatado = datetime.strptime(str(c[3]), '%Y-%m-%d').strftime('%d/%m/%Y')
                    escritor.writerow([c[0], c[1], c[2], nascimento_formatado, c[4], c[5], c[6]])

            print(f"Arquivo '{caminho}' gerado com sucesso.")
        except Exception as e:
            print("Erro ao exportar clientes para CSV:", e)
        finally:
            cursor.close()
            conn.close()

    def exportar_apolices_csv(self, nome_arquivo='apolices_sompo.csv'):
        try:
            os.makedirs('csv', exist_ok=True)
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT numero, cliente_id, tipo_seguro, dados_seguro, valor_segurado,
                       valor_mensal, vigencia, data_emissao, status FROM apolices
            """)
            apolices = cursor.fetchall()

            caminho = os.path.join('csv', nome_arquivo)
            with open(caminho, mode='w', newline='', encoding='utf-8') as arquivo_csv:
                escritor = csv.writer(arquivo_csv)
                escritor.writerow([
                    'Número da Apólice', 'ID do Cliente', 'Tipo de Seguro', 'Informações Adicionais',
                    'Valor Segurado (R$)', 'Mensalidade (R$)', 'Vigência', 'Data de Emissão', 'Status'
                ])
                for a in apolices:
                    data_emissao = datetime.strptime(str(a[7]), '%Y-%m-%d').strftime('%d/%m/%Y')
                    escritor.writerow([
                        a[0], a[1], a[2], a[3],
                        f"R$ {a[4]:,.2f}", f"R$ {a[5]:,.2f}", a[6],
                        data_emissao, a[8].capitalize()
                    ])

            print(f"Arquivo '{caminho}' gerado com sucesso.")
        except Exception as e:
            print("Erro ao exportar apólices para CSV:", e)
        finally:
            cursor.close()
            conn.close()

    def exportar_sinistros_csv(self, nome_arquivo='sinistros_sompo.csv'):
        try:
            os.makedirs('csv', exist_ok=True)
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT apolice_numero, descricao, data_ocorrencia, status FROM sinistros")
            sinistros = cursor.fetchall()

            caminho = os.path.join('csv', nome_arquivo)
            with open(caminho, mode='w', newline='', encoding='utf-8') as arquivo_csv:
                escritor = csv.writer(arquivo_csv)
                escritor.writerow(['Número da Apólice', 'Descrição', 'Data da Ocorrência', 'Status'])
                for s in sinistros:
                    data_ocorrencia = datetime.strptime(str(s[2]), '%Y-%m-%d').strftime('%d/%m/%Y')
                    escritor.writerow([s[0], s[1], data_ocorrencia, s[3].capitalize()])

            print(f"Arquivo '{caminho}' gerado com sucesso.")
        except Exception as e:
            print("Erro ao exportar sinistros para CSV:", e)
        finally:
            cursor.close()
            conn.close()

def menu():
    sompo = sompo_seguradora()
    while True:
        print("\n------ sompo seguros - menu ------")
        print("1. cadastrar novo cliente")
        print("2. emitir nova apólice")
        print("3. registrar sinistro")
        print("4. visualizar relatório geral")
        print("5. consultar sinistros por cpf")
        print("6. exportar dados para CSV")
        print("0. sair")
        opcao = input("escolha uma opção: ")

        if opcao == "1":
            nome = input("nome completo: ")
            cpf = input_cpf()
            nascimento = input("data de nascimento (aaaa-mm-dd): ")
            endereco = input("endereço completo: ")
            telefone = input("telefone: ")
            email = input("email: ")
            sompo.cadastrar_cliente(nome, cpf, nascimento, endereco, telefone, email)

        elif opcao == "2":
            cpf = input_cpf()
            print("tipos de seguro disponíveis: automóvel, residencial, vida, empresarial, agrícola, transportes")
            tipo = input("tipo de seguro: ")
            dados = input("informações adicionais (modelo do carro, endereço, cultura, etc): ")
            valor = float(input("valor segurado (r$): "))
            vigencia = input("vigência (ex: 12 meses): ")
            sompo.emitir_apolice(cpf, tipo, dados, valor, vigencia)

        elif opcao == "3":
            numero_apolice = input("número da apólice: ")
            descricao = input("descrição do sinistro: ")
            sompo.registrar_sinistro(numero_apolice, descricao)

        elif opcao == "4":
            sompo.relatorio_geral()

        elif opcao == "5":
            cpf = input_cpf()
            sompo.sinistros_por_cliente(cpf)

        elif opcao == "6":
            sompo.exportar_clientes_csv()
            sompo.exportar_apolices_csv()
            sompo.exportar_sinistros_csv()

        elif opcao == "0":
            print("encerrando sistema sompo seguros.")
            break
        else:
            print("opção inválida. tente novamente.")

if __name__ == "__main__":
    criar_banco_e_tabelas()
    menu()