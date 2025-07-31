from abc import ABC, abstractmethod
from datetime import datetime
import textwrap

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor <= 0:
            print("\n Valor Inválido!")
            return False
        if valor > self._saldo:
            print("\n Saldo Insuficiente!")
            return False

        self._saldo -= valor
        print("\n Saque realizado com sucesso!")
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("\n ======== Valor Inválido!!! ========")
            return False

        self._saldo += valor
        print("\n ======== DEPÓSITO REALIZADO COM SUCESSO! ========")
        return True

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques
        self._saques_realizados = 0

    def sacar(self, valor):
        if self._saques_realizados >= self._limite_saques:
            print("\n ======== LIMITE DE SAQUES EXCEDIDO! ========")
            return False
        if valor <= 0 or valor > (self._saldo + self._limite):
            print("\n ======== VALOR INVÁLIDO OU LIMITE EXCEDIDO! ========")
            return False

        self._saldo -= valor
        self._saques_realizados += 1
        print("\n ======== SAQUE REALIZADO COM SUCESSO! ========")
        return True

    def __str__(self):
        return f"""
            Agência: \t{self.agencia}
            C/C: \t\t{self.numero}
            Titular: \t{self.cliente.nome}
        """

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        })

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self._valor):
            conta.historico.adicionar_transacao(self)

def menu():
    menu = """\n
    =================MENU==================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))

def criar_usuario(usuarios):
    cpf = input("Informe o CPF (somente número): ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print("Usuário existente!")
        return

    nome = input("Nome completo: ")
    data_nascimento = input("Data de nascimento (dd-mm-aaaa): ")
    endereco = input("Endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    novo_usuario = PessoaFisica(nome, data_nascimento, cpf, endereco)
    usuarios.append(novo_usuario)
    print("Usuário criado com sucesso!")

def filtrar_usuario(cpf, usuarios):
    for usuario in usuarios:
        if isinstance(usuario, PessoaFisica) and usuario.cpf == cpf:
            return usuario
    return None

def criar_conta(numero_conta, usuarios, contas):
    cpf = input("Informe o CPF do usuário: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario:
        print("Usuário não encontrado!")
        return

    conta = ContaCorrente(numero_conta, usuario)
    usuario.adicionar_conta(conta)
    contas.append(conta)
    print("==== CONTA CRIADA COM SUCESSO! ========")

def listar_contas(contas):
    for conta in contas:
        print("=" * 50)
        print(f"Agência:\t\t{conta.agencia}")
        print(f"Conta:\t\t{conta.numero}")
        print(f"Titular:\t{conta.cliente.nome}")

def exibir_extrato(conta):
    print("\n======== EXTRATO ========")
    transacoes = conta.historico.transacoes
    if not transacoes:
        print("Não foram realizadas movimentações.")
    else:
        for t in transacoes:
            print(f"{t['data']} - {t['tipo']}: R$ {t['valor']:.2f}")
    print(f"\nSaldo atual: R$ {conta.saldo:.2f}")
    print("=====================================")

def main():
    usuarios = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            cpf = input("Informe seu CPF: ")
            cliente = filtrar_usuario(cpf, usuarios)

            if not cliente:
                print("Cliente não encontrado.")
                continue
            if not cliente.contas:
                print("Você ainda não possui conta. Crie uma conta primeiro.")
                continue

            valor = float(input("Informe o valor do depósito: "))
            transacao = Deposito(valor)
            cliente.realizar_transacao(cliente.contas[0], transacao)

        elif opcao == "s":
            cpf = input("Informe seu CPF: ")
            cliente = filtrar_usuario(cpf, usuarios)

            if not cliente:
                print("Cliente não encontrado!")
                continue

            if not cliente.contas:
                print("Você ainda não possui conta. Crie uma conta primeiro. ")
                continue
            
            valor = float(input("Informe o valor do saque: "))
            transacao = Saque(valor)
            cliente.realizar_transacao(cliente.contas[0], transacao)

        elif opcao == "e":
            cpf = input("Informe seu CPF: ")
            cliente = filtrar_usuario(cpf, usuarios)

            if not cliente:
                print("Cliente não encontrado!")
                continue
            exibir_extrato(cliente.contas[0])

        elif opcao == "nu":
            criar_usuario(usuarios)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, usuarios, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            print("Saindo do sistema...")
            break

        else:
            print("Opção inválida, tente novamente!")

if __name__ == "__main__":
    main()
