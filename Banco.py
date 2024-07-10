import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime

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
        if valor > self._saldo:
            print("\n *** ---- OPERAÇÃO FALHOU! Você não possui saldo suficiente. ---- ***")
            return False
        
        if valor <= 0:
            print("\n *** OPERAÇÃO FALHOU! O valor informado não é válido. ***")
            return False

        self._saldo -= valor 
        print("\n *** ---- Saque realizado com sucesso! ---- ***")
        return True
        
    def depositar(self, valor):
        if valor <= 0:
            print("\n *** ---- OPERAÇÃO FALHOU! O valor informado não é válido. ---- ***")
            return False
        
        self._saldo += valor 
        print("\n *** ---- Depósito realizado com sucesso! ---- ***")
        return True
    
    def __str__(self):
        return f"""
        Agência:\t{self.agencia}
        C/C:\t\t{self.numero}
        Titular:\t{self.cliente.nome}
        """
            
class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        if valor > self._saldo + self.limite:
            print("\n *** ---- OPERAÇÃO FALHOU! O valor informado excede o limite. ---- ***")
            return False

        if len(self.historico.transacoes) >= self.limite_saques:
            print("\n *** ---- OPERAÇÃO FALHOU! Número máximo de saques excedido. ---- ***")
            return False

        return super().sacar(valor)
            
    def __str__(self):
        return super().__str__()

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
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        })

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor 
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def menu():
    menu_text = """
======= Menu ======= 
[1] \tDepósito 
[2] \tSaque 
[3] \tExtrato
[4] \tNova Conta
[5] \tListar Contas
[6] \tNovo Usuário 
[7] \tSair
=> """
    return input(textwrap.dedent(menu_text))

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n ---- Cliente não possui conta! ---- ")
        return None
    
    return cliente.contas[0]

def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n ---- Cliente não encontrado! ---- ")
        return
    
    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)
    
    conta = recuperar_conta_cliente(cliente)
    if not conta: 
        return 
    
    cliente.realizar_transacao(conta, transacao)
    
def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n ---- Cliente não encontrado! ---- ")
        return
    
    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return 
    cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n ---- Cliente não encontrado! ---- ")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n=============== EXTRATO ===============")
    transacoes = conta.historico.transacoes

    if not transacoes:
        print("Não foram realizadas movimentações")
    else:
        for transacao in transacoes:
            print(f"{transacao['tipo']}: R$ {transacao['valor']:.2f}")

    print(f"\nSaldo: R$ {conta.saldo:.2f}")
    print("=======================================")

def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente números): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n Já existe usuário com esse CPF!")
        return 
    
    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço completo: ")

    novo_cliente = PessoaFisica(nome, data_nascimento, cpf, endereco)
    clientes.append(novo_cliente)

    print("=== Usuário criado com sucesso! ===")

def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do usuário: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n === Cliente não encontrado, fluxo de criação de conta encerrado! ===")
        return
    
    conta = ContaCorrente.nova_conta(cliente, numero_conta)
    contas.append(conta)
    cliente.adicionar_conta(conta)

    print("\n=== Conta criada com sucesso! ===")

def listar_contas(contas):
    if not contas:
        print("\nNenhuma conta cadastrada ainda.")
        return
    
    print("\n=== LISTA DE CONTAS ===")
    for conta in contas:
        print("=" * 30)
        print(conta)

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "1":
            depositar(clientes)

        elif opcao == "2":
            sacar(clientes)

        elif opcao == "3":
            exibir_extrato(clientes)
        
        elif opcao == "4":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "5":
            listar_contas(contas)

        elif opcao == "6":
            criar_cliente(clientes)
        
        elif opcao == "7":
            print("\nSaindo...")
            break
        
        else:
            print("Operação inválida, favor selecionar novamente a operação desejada.")

if __name__ == "__main__":
    main()
