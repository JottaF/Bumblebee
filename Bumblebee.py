import re
import logging
import PySimpleGUI as sg
from time import sleep, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from threading import Thread

class LoginScreen:
    def __init__(self):
        self.user = None
        self.password = None

        sg.theme('DarkGrey13')

        layout = [
            [sg.Text('Usuário:',size=(7,0)), sg.InputText(key='user', size=(15,0))],
            [sg.Text('Senha:',size=(7,0)),sg.InputText(key='password', password_char='*',size=(15,0))],
            [sg.Button('Entrar', bind_return_key=True), sg.Button('Cancel')]
        ]

        self.window = sg.Window('Login', layout)

    def login(self):
        event, values = self.window.read()

        if event == 'Entrar':
            self.user = values['user']
            self.password = values['password']

            return [self.user, self.password]

        return None
    
    def close(self):
        self.window.close()


class Controller:
    arq = open('ics.txt', 'r')
    content = arq.read().split('\n')
    arq.close()
    
    __icsList = []
    __concluidos = []
    __inicio = time()
    __fim = None

    for i in content:
        try:
            __icsList.append(i.split('=')[2])
        except:
            pass

    def __init__(self):
        self.window = LoginScreen()
        self.login = self.window.login()
        self.window.close()

        self.user = self.login[0]
        self.password = self.login[1]

        self.navigator = webdriver.Chrome()
        self.navigator.maximize_window()

        self.navigator.get('https://suportedti.agu.gov.br/otrs/index.pl')

        sleep(0.2)
        self.navigator.find_element(By.NAME, 'User').send_keys(self.user)
        self.navigator.find_element(By.NAME, 'Password').send_keys(self.password + Keys.ENTER)

        sleep(0.2)
        self.user = None
        self.password = None

    def pesquisarPorLink(self, chamado):
        self.navigator.get('https://suportedti.agu.gov.br/otrs/index.pl?Action=AgentTicketZoom;TicketID='+ str(chamado))
        sleep(0.5)
        self.navigator.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    
    def adicionarIc(self, chamado):
        self.navigator.get('https://suportedti.agu.gov.br/otrs/index.pl?Action=AgentLinkObject;SourceObject=Ticket;SourceKey='+ str(chamado))
        sleep(0.2)

    def servidoresVirtuais(self, servidor):
        self.navigator.find_element(By.ID, 'TargetIdentifier_Search').send_keys('servidores virtuais')
        sleep(0.2)
        self.navigator.find_element(By.ID, 'TargetIdentifier_Search').send_keys(Keys.ARROW_DOWN + Keys.ARROW_DOWN + Keys.ENTER)
        sleep(0.2)

        self.navigator.find_element(By.ID, 'SEARCH::Name').send_keys(servidor + Keys.ENTER)
        sleep(0.2)

        self.navigator.find_element(By.ID, 'LinkTargetKeys').click()
        self.navigator.find_element(By.ID, 'AddLinks').click()

    def bibliotecaDeSoftware(self):
        self.navigator.find_element(By.ID, 'TargetIdentifier_Search').send_keys('desktop')
        sleep(0.2)
        self.navigator.find_element(By.ID, 'TargetIdentifier_Search').send_keys(Keys.ARROW_DOWN + Keys.ARROW_DOWN + Keys.ENTER)
        sleep(0.2)

        self.navigator.find_element(By.ID, 'SEARCH::Name').send_keys('biblioteca' + Keys.ENTER)
        sleep(0.2)

        self.navigator.find_element(By.ID, 'LinkTargetKeys').click()
        self.navigator.find_element(By.ID, 'AddLinks').click()

    def patrimonio(self, patrimonio):
        self.navigator.find_element(By.ID, 'TargetIdentifier_Search').send_keys('desktop')
        sleep(0.2)
        self.navigator.find_element(By.ID, 'TargetIdentifier_Search').send_keys(Keys.ARROW_DOWN + Keys.ARROW_DOWN + Keys.ENTER)
        sleep(0.2)

        self.navigator.find_element(By.ID, 'SEARCH::Name').send_keys(patrimonio + Keys.ENTER)
        sleep(0.2)

        self.navigator.find_element(By.ID, 'LinkTargetKeys').click()
        self.navigator.find_element(By.ID, 'AddLinks').click()

    def caixasPostais(self, usuario):
        self.navigator.find_element(By.ID, 'TargetIdentifier_Search').send_keys('caixas postais')
        sleep(0.2)
        self.navigator.find_element(By.ID, 'TargetIdentifier_Search').send_keys(Keys.ARROW_DOWN + Keys.ARROW_DOWN + Keys.ENTER)
        sleep(0.2)

        self.navigator.find_element(By.ID, 'SEARCH::Name').send_keys(usuario + Keys.ENTER)
        sleep(0.2)

        self.navigator.find_element(By.ID, 'LinkTargetKeys').click()
        self.navigator.find_element(By.ID, 'AddLinks').click()
    
    def getUsuario(self):
        try:
            usuario = self.navigator.find_elements(By.CLASS_NAME,'Sender')
            return usuario[-1].text
        except:
            return 'Não foi possível coletar o nome do usuário'
    
    def getInfoChamado(self):
        try:
            frame = self.navigator.find_elements(By.TAG_NAME, 'iframe')
            self.navigator.switch_to.frame(frame[-1])
            info = self.navigator.find_element(By.TAG_NAME, 'body')
            self.navigator.switch_to.default_content
            return info.text
        except:
            return None

    def verificaPatrimonio(self):
        try:
            info = self.getInfoChamado()
            rex = "\D*([0-5]\d{2}[.]?\d{3,5})"
            patrimonio = re.findall(rex, info)
            for i in range(len(patrimonio)):
                patrimonio[i] = patrimonio[i].replace('.','')
            return patrimonio
        except:
            return None
    
    def addConcluido(self, chamdo):
        self.__concluidos.append(chamdo)
    
    def removeConcluido(self):
        self.__concluidos.pop()
    
    def removerICsConcluidosDaLista(self):
        try:
            self.__icsList = list(set(self.__icsList).difference(set(self.__concluidos)))

            arq = open('ics.txt', 'w')
            for i in self.__icsList:
                if i == '' or i == None:
                    return
                arq.write('https://suportedti.agu.gov.br/otrs/index.pl?Action=AgentTicketZoom;TicketID='+ str(i)+'\n') if i != self.__icsList[-1] else arq.write('https://suportedti.agu.gov.br/otrs/index.pl?Action=AgentTicketZoom;TicketID='+str(i))
            arq.close()
        except:
            logging.info("Erro ao remover IC's concluídos da lista.")
    
    def criarListaConcluidos(self):
        try:
            arq = open('chamados_concluidos.txt', 'w')
            arq.write("Foram inseridos {} IC's.\n".format(self.getConcluidos()))

            for i in self.__concluidos:
                arq.write('https://suportedti.agu.gov.br/otrs/index.pl?Action=AgentTicketZoom;TicketID='+ str(i)+'\n')

            arq.close()
        except:
            logging.info("Erro ao criar lista de concluídos.")
    
    def getConcluidos(self):
        return str(len(self.__concluidos))
    
    def getTotal(self): 
        return str(len(self.__icsList))
    
    def getRestantes(self):
        return str(len(self.__icsList) - len(self.__concluidos))
    
    def getChamado(self, index):
        return str(self.__icsList[index])
    
    def chamados(self):
        return self.__icsList
    
    def setFim(self):
        self.__fim = time()
    
    def getDuracao(self):
        return (self.__fim - self.__inicio) / 60

    def verificarLogin(self):
        try:
            self.navigator.find_element(By.CLASS_NAME, 'ErrorBox')
            return False
        except:
            return True
    
    def fecharNavegador(self):
        self.navigator.close()

class SalvarProcesso(Thread):
    def __init__(self, controller):
        Thread.__init__(self)
        self.controller = controller

    def run(self):
        self.controller.removerICsConcluidosDaLista()
        self.controller.criarListaConcluidos()
        print('Arquivos atualizados')

if __name__ == '__main__':
    controller = Controller()

    option = -1
    index = 0
    button = None
    usuario = None

    chamado = controller.getChamado(index)

    sg.theme('DarkGrey13')
    layout = [
        [sg.Text('Escolha o IC a ser inserido:', size=(20,0))],
        [sg.Text('1 - Reset de Senha')],
        [sg.Text('2 - Biblioteca de Software')],
        [sg.Text('3 - Alteração na conta')],
        [sg.Text('4 - Desativar conta')],
        [sg.Text('5 - Criação de conta')],
        [sg.Text('6 - Patrimônio (Informe o patrimônio antes de escolher esta opção)'), sg.InputText(key='patrimonio', size=(15,0),)],
        [sg.Text('66 - Patrimônio(s) encontrado(s)'), sg.Combo(key = 'comboPatrimonio', values=[], size=(15,0))],
        [sg.Text('7 - Inserir manualmente'), sg.Button('Prosseguir', key='prosseguir', disabled=True)],
        [sg.Text('8 - Caixas postais')],
        [sg.Text('9 - Pular')],
        [sg.InputText(key='option', focus=True), sg.Button('Selecionar', key='selecionar', bind_return_key=True)],
        [sg.Button('Encerrar')]
    ]


    if controller.verificarLogin():
        window = sg.Window('Bumblebee', layout, finalize = True)
        total = controller.getTotal()

        while True and int(option) != 0 and index < int(total):
            chamado = controller.getChamado(index)
            controller.pesquisarPorLink(chamado)
            usuario = controller.getUsuario()
            
            try:
                if index != 0:
                    if value['patrimonio'] != '' or value['patrimonio'] != None:
                        window['patrimonio']('') #Limpa o campo patrimônio
                    if value['comboPatrimonio'] or value['comboPatrimonio'] != None:
                        window['comboPatrimonio']([])
                    window.refresh()
            except:
                pass

            patrimonio = controller.verificaPatrimonio()
            if patrimonio:
                try:
                    window['comboPatrimonio'].Update(values = patrimonio)
                    window['comboPatrimonio'](patrimonio[0])
                except:
                    pass

            button, value = window.read()

            if button == 'Encerrar' or button == sg.WIN_CLOSED:
                controller.removerICsConcluidosDaLista()
                break

            option = int(value['option']) if value['option'] != '' else -1

            window['option']('')
            window.refresh()

            if option >= 0 and option <= 9 or option == 66:
                if option != 0:
                    if option != 9: controller.adicionarIc(chamado)
                    controller.addConcluido(chamado)
                    
                    try:
                        if option == 1:
                            controller.servidoresVirtuais('SDFURA0031')
                        elif option == 2:
                            controller.bibliotecaDeSoftware()
                        elif option == 3:
                            controller.servidoresVirtuais('SDF0432')
                        elif option == 4:
                            controller.servidoresVirtuais('SDF0814')
                        elif option == 5:
                            controller.servidoresVirtuais('SDFURA0117')
                        elif option == 6:
                            patrimonio = value['patrimonio']
                            controller.patrimonio(patrimonio)
                            window.refresh()
                        elif option == 66:
                            patrimonio = value['comboPatrimonio']
                            controller.patrimonio(patrimonio)
                            window.refresh()
                        elif option == 7:
                            window['prosseguir'].Update(disabled = False)
                            window['selecionar'].Update(disabled = True)
                            while button != 'prosseguir':
                                button, value = window.read()
                            window['prosseguir'].Update(disabled = True)
                            window['selecionar'].Update(disabled = False)
                        elif option == 8:
                            controller.caixasPostais(str(usuario))
                        elif option > 9:
                            controller.removeConcluido()
                    except:
                        controller.removeConcluido()
                        
                        index -= 1
                    
                    index += 1
            
            if index != 0 and index % 5 == 0:        # A cada 5 IC's inseridos o programa atualizará 
                SalvarProcesso(controller).start()   # os arquivos ics.txt e chamados_concluidos.txt
                total = controller.getTotal()
                index = 0

        controller.removerICsConcluidosDaLista()

    else:
        layout = [
            [sg.Text('Falha ao efetuar login!!!', text_color='red',size=(20,3))],
        ]

        window = sg.Window('Falha', layout)

        while True:
            event, value = window.read()

            if event == sg.WIN_CLOSED:
                break
            


    controller.criarListaConcluidos()
    controller.setFim()
    duracao = controller.getDuracao()

    layout = [
        [sg.Text('Inclusão de IC finalizada!!!', text_color='green',size=(20,3))],
        [sg.Text('Duração: '), sg.Text(f'{duracao:.2f} minutos')],
    ]

    window = sg.Window('Finalizado', layout)

    event, value = window.read()


    controller.fecharNavegador()
