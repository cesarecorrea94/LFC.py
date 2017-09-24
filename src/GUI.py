#coding: utf-8
'''
Created on 16/06/2017

@author: cesar
'''
from gi.repository import Gtk
from datetime import datetime, timedelta
from time import sleep
from AF import AF

letrasmin = [chr(c) for c in range(ord('a'),ord('z')+1)]
letrasmai = [chr(c) for c in range(ord('A'),ord('Z')+1)]
digitos = [str(i) for i in range(10)]

class GUI(object):
    '''
    Responsável pela comunicação com o usuário.
    @cvar _builder: Responsável por carregar a interface usuário, e manter referência a seus widgets
    @type builder: Gtk.Builder
    @cvar tabs: Responsável por manter os builders das interfaces AF
    @type tabs: list
    @cvar numeracao: Contador para a definição do nome do próximo AF
    @type numeracao: int
    '''
    _builder = None
    tabs = []
    numeracao = 0
    
    @staticmethod
    def next_M():
        GUI.numeracao += 1
        return 'M'+str(GUI.numeracao)
    
    @staticmethod
    def new_builder_tab():
        builder = Gtk.Builder()
        builder.add_from_file("novotab.glade")
        builder.connect_signals({
                "on_novoestado_clicked": GUI.on_novoestado_clicked,
                "on_novoterminal_clicked": GUI.on_novoterminal_clicked,
                })
        return builder
    
    @staticmethod
    def on_criar_clicked(widget):
        '''
        Abre a janela de diálogo para a criação de um AF
        @param widget: widget que enviou o sinal para a chamada da rotina (o botão fechar).
        '''
        GUI._builder.get_object('dialog1').show_all()
        pass
    
    @staticmethod
    def put_AF_on_builder(builder, M):
        '''
        Coloca o AF 'M' na interface referênciada pelo 'builder'
        @param builder: classe Gtk responsável por abrir uma interface glade, e tem referência a todos os widgets de tal interface
        @type builder: Gtk.Builder
        @param M: máquina a qual deseja-se por na interface usuário
        @type M: AF
        '''
        grid = builder.get_object('grid1')
        grid.remove_row(1)
        grid.remove_column(1)
        Qs = sorted(M.get_estados())
        top = 0; left = 0
        for q in Qs:
            entry = Gtk.Entry()
            entry.set_width_chars(10)
            text = str(q)
            if q == M.S: text = "->" + text
            if q in M.finais: text = "*" + text
            entry.set_text(text)
            top += 1
            grid.attach(entry, left, top, 1, 1)
            pass
        for t in sorted(M.alfabeto()):
            entry = Gtk.Entry()
            entry.set_width_chars(10)
            entry.set_text(t)
            left += 1; top = 0
            grid.attach(entry, left, top, 1, 1)
            for q in Qs:
                qnext = M.get_pos_as_set(q, t)
                qnextfilter = ','.join([str(i) for i in qnext])
                entry = Gtk.Entry()
                entry.set_width_chars(10)
                entry.set_text(qnextfilter)
                top += 1
                grid.attach(entry, left, top, 1, 1)
                pass
            pass
        grid.show_all()
        pass
    
    @staticmethod
    def get_AF_from_builder(builder):
        '''
        Obtém-se uma máquina AF referênciada por um dado 'builder'
        @param builder: classe Gtk responsável por abrir uma interface glade, e tem referência a todos os widgets de tal interface
        @type builder: Gtk.Builder
        @return: a máquina na interface referênciada pelo 'builder'
        @rtype: AF
        '''
        grid = builder.get_object('grid1')
        alfabeto = []
        top = 0; left = 0
        while True:
            left += 1
            try:t = grid.get_child_at(left, top).get_text()
            except:break
            tfilter = ''.join([i for i in t
                               if i in letrasmin
                               or i in digitos
                               #or i == '&'
                               ]) # apenas letras minusculas, digitos ou epsilon
            #if tfilter != '&': tfilter = tfilter.replace('&', '') # se não for 1 epsilon, remove todos os epsilons
            alfabeto.append(tfilter)
            pass
        M = AF()
        M.tabela = {}
        while True:
            top += 1; left = 0
            try:q = grid.get_child_at(left, top).get_text()
            except:break
            qfilter = ''.join([i for i in q
                               if i in letrasmai]) # apenas letras maiusculas
            if qfilter: # if is not ''
                M.tabela[qfilter] = {}
                if "->" in q: M.S = qfilter
                if "*" in q: M.finais.add(qfilter)
                for t in alfabeto:
                    left += 1
                    if (t in letrasmin
                        or t in digitos
                        #or t == '&'
                        ):
                        qnext = grid.get_child_at(left, top).get_text()
                        qnextfilter = ''.join([i for i in qnext
                                               if i in letrasmai
                                               or i == ',']) # apenas letras maiusculas ou ',' (AFND)
                        qnextfilter = set(qnextfilter.split(','))
                        qnextfilter.discard('')
                        M.tabela[qfilter][t] = qnextfilter
                        pass
                    pass
                pass
            pass
        return M
    
    @staticmethod
    def get_page_number_from_M_entry(notebook):
        '''
        Obtém o nome de máquina referenciado pelo usuário,
        que está na entrada responsável pela informação de outro AF nas operações que envolvem 2 AF
        Procura pela página de interface que corresponde ao nome de máquina obtido, e retorna seu índice no 'notebook'
        @param notebook: widget responsável por manter todas as interfaces AF
        @type notebook: Gtk.Notebook
        @return: índice da máquina passada pelo usuário no 'notebook'
        @rtype: int
        @raise None: Caso a máquina referenciada não exista
        '''
        M2label = GUI._builder.get_object('M').get_text()
        for nth in range(1, notebook.get_n_pages()):
            page = notebook.get_nth_page(nth)
            label = notebook.get_tab_label_text(page)
            if M2label == label: return nth
            pass
        raise None
    
    @staticmethod
    def get_AF_on_current_page(notebook):
        '''
        Obtém o AF na atual página de interface AF
        @param notebook: widget responsável por manter todas as interfaces AF
        @type notebook: Gtk.Notebook
        @return: (o nome (não a descrição) do autômato na atual página de interface AF,
                o AF na atual página de interface AF)
        @rtype: (str, AF)
        @raise None: Caso a aba atual seja do Manual
        '''
        currentpage = notebook.get_current_page()
        if currentpage == 0: raise None
        page = notebook.get_nth_page(currentpage)
        M1label = notebook.get_tab_label_text(page)
        builder = GUI.tabs[currentpage-1]
        M1 = GUI.get_AF_from_builder(builder)
        return (M1label, M1)
    
    @staticmethod
    def get_current_tab_label(notebook):
        '''
        Obtém o nome (não a descrição) do autômato na atual página de interface AF
        @param notebook: widget responsável por manter todas as interfaces AF
        @type notebook: Gtk.Notebook
        @return: o nome do atual AF
        @rtype: str
        '''
        currentpage = notebook.get_current_page()
        page = notebook.get_nth_page(currentpage)
        return notebook.get_tab_label_text(page)
    
    @staticmethod
    def on_novoestado_clicked(widget):
        '''
        Cria um nova linha na tabela de transição da atual página de interface AF
        @param widget: widget que enviou o sinal para a chamada da rotina (o botão fechar).
        '''
        notebook = GUI._builder.get_object('notebook1')
        currentpage = notebook.get_current_page()
        builder = GUI.tabs[currentpage-1]
        grid = builder.get_object('grid1')
        top = 0; left = 0
        while True:
            top += 1
            try:grid.get_child_at(left, top).get_text()
            except:break
            pass
        while True:
            try:grid.get_child_at(left, top-1).get_text()
            except:break
            entry = Gtk.Entry()
            entry.set_width_chars(10)
            grid.attach(entry, left, top, 1, 1)
            left += 1
            pass
        grid.show_all()
        pass
    
    @staticmethod
    def on_novoterminal_clicked(widget):
        '''
        Cria um nova coluna na tabela de transição da atual página de interface AF
        @param widget: widget que enviou o sinal para a chamada da rotina (o botão fechar).
        '''
        notebook = GUI._builder.get_object('notebook1')
        currentpage = notebook.get_current_page()
        builder = GUI.tabs[currentpage-1]
        grid = builder.get_object('grid1')
        top = 0; left = 0
        while True:
            left += 1
            try:grid.get_child_at(left, top).get_text()
            except:break
            pass
        while True:
            try:grid.get_child_at(left-1, top).get_text()
            except:break
            entry = Gtk.Entry()
            entry.set_width_chars(10)
            grid.attach(entry, left, top, 1, 1)
            top += 1
            pass
        grid.show_all()
        pass
    
    @staticmethod
    def on_criarER_clicked(widget):
        '''
        Cria um AF para uma dada ER (será obtida pelo 'GUI._builder'). 
        Cria uma nova página de interface, e coloca tal AF
        @param widget: widget que enviou o sinal para a chamada da rotina (o botão fechar).
        '''
        builder = GUI.new_builder_tab()
        ER = GUI._builder.get_object('ER').get_text()
        GUI.put_AF_on_builder(builder, AF(ER))
        builder.get_object('descrição').set_text(ER)
        
        notebook = GUI._builder.get_object('notebook1')
        notebook.append_page(builder.get_object('box1'),
                             Gtk.Label(GUI.next_M())
                             )
        notebook.set_current_page(notebook.get_n_pages()-1)
        
        GUI.tabs.append(builder)
        GUI._builder.get_object('dialog1').hide()
        pass
    
    @staticmethod
    def on_criarAF_clicked(widget):
        '''
        Cria uma nova página de interface para AF
        @param widget: widget que enviou o sinal para a chamada da rotina (o botão fechar).
        '''
        builder = GUI.new_builder_tab()
        builder.get_object('descrição').set_text('AF vazio')
        
        notebook = GUI._builder.get_object('notebook1')
        notebook.append_page(builder.get_object('box1'),
                             Gtk.Label(GUI.next_M())
                             )
        notebook.set_current_page(notebook.get_n_pages()-1)
        
        GUI.tabs.append(builder)
        GUI._builder.get_object('dialog1').hide()
        pass
    
    @staticmethod
    def on_deletar_clicked(widget):
        '''
        Remove a atual página de interface para AF
        @param widget: widget que enviou o sinal para a chamada da rotina (o botão fechar).
        '''
        notebook = GUI._builder.get_object('notebook1')
        currentpage = notebook.get_current_page()
        if currentpage == 0: return
        notebook.remove_page(currentpage)
        builder = GUI.tabs.pop(currentpage-1)
        del builder # deletar todos os widgets no builder (mais tarde o garbage collector o fará)
        pass
    
    @staticmethod
    def on_determinizar_clicked(widget):
        '''
        Obtém o AF na atual página de interface AF, e determiniza-o
        Cria um nova página de interface AF e coloca o novo AF obtido
        @param widget: widget que enviou o sinal para a chamada da rotina (o botão fechar).
        '''
        notebook = GUI._builder.get_object('notebook1')
        label, M = GUI.get_AF_on_current_page(notebook)
        
        builder = GUI.new_builder_tab()
        GUI.put_AF_on_builder(builder, M.determinizar())
        builder.get_object('descrição').set_text(label + " determinizado")
        
        notebook.append_page(builder.get_object('box1'),
                             Gtk.Label(GUI.next_M())
                             )
        notebook.set_current_page(notebook.get_n_pages()-1)
        
        GUI.tabs.append(builder)
        GUI._builder.get_object('dialog1').hide()
        pass
    
    @staticmethod
    def on_minimizar_clicked(widget):
        '''
        Obtém o AF na atual página de interface AF, e minimiza-o (se necessário, chama 'GUI.on_determinizar_clicked')
        Cria um nova página de interface AF e coloca o novo AF obtido
        @param widget: widget que enviou o sinal para a chamada da rotina (o botão fechar).
        '''
        notebook = GUI._builder.get_object('notebook1')
        label, M = GUI.get_AF_on_current_page(notebook)
        if not M.is_deterministico():
            GUI.on_determinizar_clicked(widget)
            label, M = GUI.get_AF_on_current_page(notebook)
            pass
        
        builder = GUI.new_builder_tab()
        GUI.put_AF_on_builder(builder, M.minimizar())
        builder.get_object('descrição').set_text(label + " minimizado")
        
        notebook.append_page(builder.get_object('box1'),
                             Gtk.Label(GUI.next_M())
                             )
        notebook.set_current_page(notebook.get_n_pages()-1)
        
        GUI.tabs.append(builder)
        GUI._builder.get_object('dialog1').hide()
        pass
    
    @staticmethod
    def on_complemento_clicked(widget):
        '''
        Obtém o AF na atual página de interface AF, e complementa-o (se necessário, chama 'GUI.on_determinizar_clicked')
        Cria um nova página de interface AF e coloca o novo AF obtido
        @param widget: widget que enviou o sinal para a chamada da rotina (o botão fechar).
        '''
        notebook = GUI._builder.get_object('notebook1')
        label, M = GUI.get_AF_on_current_page(notebook)
        if not M.is_deterministico():
            GUI.on_determinizar_clicked(widget)
            label, M = GUI.get_AF_on_current_page(notebook)
            pass
        
        builder = GUI.new_builder_tab()
        GUI.put_AF_on_builder(builder, M.complemento())
        builder.get_object('descrição').set_text(label + " complemento")
        
        notebook = GUI._builder.get_object('notebook1')
        notebook.append_page(builder.get_object('box1'),
                             Gtk.Label(GUI.next_M())
                             )
        notebook.set_current_page(notebook.get_n_pages()-1)
        
        GUI.tabs.append(builder)
        GUI._builder.get_object('dialog1').hide()
        pass
    
    @staticmethod
    def on_uniao_clicked(widget):
        '''
        Obtém o nome de máquina referenciado pelo usuário,
        que está na entrada responsável pela informação de outro AF nas operações que envolvem 2 AF
        Obtém o AF na atual página de interface AF, e realiza a união deste com o AF referenciado pelo usuário
        Cria um nova página de interface AF e coloca o novo AF obtido
        @param widget: widget que enviou o sinal para a chamada da rotina (o botão fechar).
        '''
        notebook = GUI._builder.get_object('notebook1')
        M2_page_number = GUI.get_page_number_from_M_entry(notebook)
        
        M1label, M1 = GUI.get_AF_on_current_page(notebook)
        notebook.set_current_page(M2_page_number)
        M2label, M2 = GUI.get_AF_on_current_page(notebook)
        
        builder = GUI.new_builder_tab()
        GUI.put_AF_on_builder(builder, M1.uniao(M2))
        builder.get_object('descrição').set_text(M1label + " U " + M2label)
        
        notebook.append_page(builder.get_object('box1'),
                             Gtk.Label(GUI.next_M())
                             )
        notebook.set_current_page(notebook.get_n_pages()-1)
        
        GUI.tabs.append(builder)
        GUI._builder.get_object('dialog1').hide()
        pass
    
    @staticmethod
    def on_interseccao_clicked(widget):
        '''
        Obtém o nome de máquina referenciado pelo usuário,
        que está na entrada responsável pela informação de outro AF nas operações que envolvem 2 AF
        Obtém o AF na atual página de interface AF, e realiza a intersecção deste com o AF referenciado pelo usuário
        A intersecção simula a chamada de outras rotinas responsáveis pelas operações que a compõem.
        @param widget: widget que enviou o sinal para a chamada da rotina (o botão fechar).
        '''
        notebook = GUI._builder.get_object('notebook1')
        M2_page_number = GUI.get_page_number_from_M_entry(notebook)
        
        M1label = GUI.get_current_tab_label(notebook)
        
        GUI.on_complemento_clicked(widget)
        M1Clabel = GUI.get_current_tab_label(notebook)
        
        notebook.set_current_page(M2_page_number)
        M2label = GUI.get_current_tab_label(notebook)
        
        GUI.on_complemento_clicked(widget) # M2C
        
        GUI._builder.get_object('M').set_text(M1Clabel) # simular o pedido de união de M2C com M1C
        GUI.on_uniao_clicked(widget)
        GUI._builder.get_object('M').set_text(M2label) # reverter a simulação
        
        GUI.on_complemento_clicked(widget)
        
        builder = GUI.tabs[-1] # last builder
        desc_entry = builder.get_object('descrição')
        desc_entry.set_text(desc_entry.get_text() + " = " + M1label + " ∩ " + M2label)
        pass
    
    @staticmethod
    def on_diferenca_clicked(widget):
        '''
        Obtém o nome de máquina referenciado pelo usuário,
        que está na entrada responsável pela informação de outro AF nas operações que envolvem 2 AF
        Obtém o AF na atual página de interface AF, e realiza a diferença deste com o AF referenciado pelo usuário
        A diferença simula a chamada de outras rotinas responsáveis pelas operações que a compõem.
        @param widget: widget que enviou o sinal para a chamada da rotina (o botão fechar).
        '''
        notebook = GUI._builder.get_object('notebook1')
        M2_page_number = GUI.get_page_number_from_M_entry(notebook)
        page = notebook.get_nth_page(M2_page_number)
        M2label = notebook.get_tab_label_text(page)
        M1label = GUI.get_current_tab_label(notebook)
        
        GUI.on_complemento_clicked(widget) # M1C
        
        GUI.on_uniao_clicked(widget) #M1C U M2
        
        GUI.on_complemento_clicked(widget)
        
        builder = GUI.tabs[-1] # last builder
        desc_entry = builder.get_object('descrição')
        desc_entry.set_text(desc_entry.get_text() + " = " + M1label + " - " + M2label)
        pass
    
    @staticmethod
    def on_diferenca_clicked_old(widget):
        '''
        Equivalente a GUI.on_diferenca_clicked, porém, fazendo por outras operações.
        Este realiza M1 - M2 = M1 ∩ complemento( M2 )
        Aquele realiza M1 - M2 = complemento( complemento( M1 ) U M2)
        Este não é executado. Está aqui só pra bonito/informação.
        '''
        notebook = GUI._builder.get_object('notebook1')
        M1label = GUI.get_current_tab_label(notebook)
        
        M2_page_number = GUI.get_page_number_from_M_entry(notebook)
        notebook.set_current_page(M2_page_number)
        M2label = GUI.get_current_tab_label(notebook)
        
        GUI.on_complemento_clicked(widget) # M2C
        
        GUI._builder.get_object('M').set_text(M1label) # simular o pedido de intersecção de M1 com M2C
        GUI.on_interseccao_clicked(widget)
        GUI._builder.get_object('M').set_text(M2label) # reverter a simulação
        
        builder = GUI.tabs[-1] # last builder
        desc_entry = builder.get_object('descrição')
        desc_entry.set_text(desc_entry.get_text() + " = " + M1label + " - " + M2label)
        pass
    
    pass
