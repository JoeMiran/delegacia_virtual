from datetime import datetime

class Usuario:
    def __init__(self, nome, email, senha, role):
        self.nome = nome
        self.email = email
        self.senha = senha   
        self.role = role     

class Vitima(Usuario):
    def registrar_ocorrencia(self, descricao):
        ocorrencia = Occurrence(self, descricao)
        occurrences.append(ocorrencia)
        return ocorrencia

    def acompanhar_ocorrencias(self):
        return [o for o in occurrences if o.vitima.email == self.email]

class Investigador(Usuario):
    def investigar(self, ocorrencia, suspeito, evidencias):
        investigacao = Investigation(ocorrencia, suspeito, evidencias, self)
        investigations.append(investigacao)
        ocorrencia.status = "Investigada"
        return investigacao

    def solicitar_pericia(self, ocorrencia, data_pericia, descricao):
        agendamento = Agendamento(ocorrencia, data_pericia, descricao)
        agendamentos.append(agendamento)
        return agendamento

class Delegado(Usuario):
    def avaliar_investigacao(self, investigacao, decisao):
        investigacao.decisao = decisao
        investigacao.ocorrencia.status = "Concluída"
        return investigacao

class Occurrence:
    id_counter = 1

    def __init__(self, vitima, descricao):
        self.id = Occurrence.id_counter
        Occurrence.id_counter += 1
        self.vitima = vitima
        self.descricao = descricao
        self.data_registro = datetime.now()
        self.status = "Nova"  

class Investigation:
    id_counter = 1

    def __init__(self, ocorrencia, suspeito, evidencias, investigador):
        self.id = Investigation.id_counter
        Investigation.id_counter += 1
        self.ocorrencia = ocorrencia
        self.suspeito = suspeito
        self.evidencias = evidencias
        self.investigador = investigador
        self.data_investigacao = datetime.now()
        self.decisao = None

class Agendamento:
    id_counter = 1

    def __init__(self, ocorrencia, data_pericia, descricao):
        self.id = Agendamento.id_counter
        Agendamento.id_counter += 1
        self.ocorrencia = ocorrencia
        self.data_pericia = data_pericia
        self.descricao = descricao
        self.status = "Agendado"  

occurrences = []      
investigations = []   
agendamentos = []     


users = {
    "vitima": Vitima("Vítima 1", "victim1@example.com", "pass", "vitima"),
    "investigador": Investigador("Investigador 1", "investigator1@example.com", "pass", "investigador"),
    "delegado": Delegado("Delegado 1", "delegate1@example.com", "pass", "delegado")
}
