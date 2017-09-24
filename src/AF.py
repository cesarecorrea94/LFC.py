#coding: utf-8
'''
Created on 16/06/2017

@author: cesar
'''
from DeSimone import DeSimone
from operator import xor

class AF(object):
    '''
    Representante de um AF
    @cvar S: estado inicial
    @type S: str
    @cvar tabela: tabela de transições
    @type tabela: dict
    @cvar finais: estados finais
    @type finais: set
    '''
    S = None
    tabela = {}
    finais = set([])

    def __init__(self, ER=None):
        '''
        Construtor de um autômato finito
        '''
        self.S = None
        self.tabela = {}
        self.finais = set([])
        if ER is not None: self.make_from_ER(ER)
    
    def __repr__(self): # const
        '''
        Retorna uma string representando este AF.
        Para debug: ao imprimir (print) este objeto, será impresso o retorno dessa função.
        @return: Uma string representando este AF.
        @rtype: str
        '''
        debug = "\n"
        debug += "-> " + repr(self.S) +"\n"
        debug += "* " + repr(self.finais) + "\n"
        for k,v in self.tabela.items():
            debug += repr(k) + " : " + repr(v) + "\n"
        return debug
    
    @staticmethod
    def get_nth_name(n):
        '''
        Função utilizada para a definição dos nomes dos estados
        Cria um nome contendo 2 letras maiúsculas, para um dado número inteiro positivo
        @param n: número identificando o nome do estado
        @type n: int
        @return: N-ésimo nome para um estado
        @rtype: str
        '''
        nletras = 1+ord('Z')-ord('A')
        qname = chr(ord('A') + n/nletras)
        qname += chr(ord('A') + n%nletras)
        return qname
    
    def get_estados(self): # const
        '''
        Retorna os estados deste AF
        @return: Os estados deste AF
        @rtype: set
        '''
        return self.tabela.keys()
    
    def get_pos_as_set(self, q, t): # const
        '''
        Retorna os próximos estados da transição δ(q,t)
        @return: Um conjunto contendo os próximos estados pela transição δ(q,t)
        @rtype: set
        '''
        try:qnext = self.tabela[q][t]
        except: return set([])
        if isinstance(qnext, str):
            if qnext == '': qnext = []
            else: qnext = [qnext]
            pass
        return set([]).union(qnext)
    
    def make_from_ER(self, ER):
        '''
        Atribui a este AF, a tabela de transições obtida pelo algoritmo de DeSimone
        Define o estado inicial, e quais serão os estados finais, pela coluna de composição
        '''
        tabela = DeSimone.DeSimone(ER)
        self.S = AF.get_nth_name(0)
        for qi, transicoes in tabela.items():
            qnow = AF.get_nth_name(qi)
            self.tabela[qnow] = {}
            if None in transicoes["composicao"]: self.finais.add(qnow)
            for t, qnexti in transicoes.items():
                if len(t) == 1: self.tabela[qnow][t] = AF.get_nth_name(qnexti)
                pass
            pass
        pass
    
    def alfabeto(self): # const
        '''
        Retorna o alfabeto deste AF
        @return: Um conjunto com os terminais aceitos por este AF
        @rtype: set
        '''
        alfabeto = set([])
        for transicoes in self.tabela.values():
            alfabeto.update(transicoes.keys())
            pass
        for i in alfabeto:
            if len(i) != 1:
                alfabeto.discard(i)
                pass
            pass
        return alfabeto
    
    def is_eLivre(self):
        return '&' not in self.alfabeto()
    
    #def transforma_eLivre(self):
    #    M = AF()
    #    for q in self.get_estados():
    #        for etransicao in self.get_pos_as_set(q, '&'):
    #            for 
    #            pass
    #        pass
    #    pass
    
    def is_deterministico(self): # const
        '''
        Verifica se este AF é determinístico
        @return: Valor verdade da identificação deste AF como determinístico
        @rtype: bool
        '''
        for transicoes in self.tabela.values():
            for t in self.alfabeto():
                try:
                    if len(transicoes[t]) > 1:
                        return False
                    pass
                except:pass
            pass
        return True
    
    def determinizar(self): # const
        '''
        Determiniza este AF
        @return: Um novo AF equivalente a este (self), e determinizado
        @rtype: AF
        '''
        M = AF()
        falta = [set([self.S])]
        qlist = list(falta)
        while falta:
            qset = falta.pop()
            qnow = AF.get_nth_name(qlist.index(qset))
            M.tabela[qnow] = {}
            if qset == set([self.S]): M.S = qnow
            if qset.intersection(self.finais): M.finais.add(qnow) # if not empty
            for t in self.alfabeto():
                M.tabela[qnow][t] = set([])
                for q in qset:
                    M.tabela[qnow][t].update(self.get_pos_as_set(q, t)) # union
                    pass
                if M.tabela[qnow][t] not in qlist:
                    qlist.append(M.tabela[qnow][t])
                    falta.append(M.tabela[qnow][t])
                    pass
                M.tabela[qnow][t] = AF.get_nth_name(qlist.index(M.tabela[qnow][t]))
                pass
            pass
        return M
    
    def get_ferteis(self): # const
        '''
        Obtém-se os estados férteis deste AF
        @return: Um conjunto contendo os estados férteis
        @rtype: set
        '''
        ferteis = set(self.finais)
        len_antes = 0
        while len_antes != len(ferteis):
            len_antes = len(ferteis)
            for qnow in self.get_estados():
                if qnow in ferteis: continue
                for t in self.alfabeto():
                    for qnext in self.get_pos_as_set(qnow, t):
                        if qnext in ferteis:
                            ferteis.add(qnow)
                            break
                        pass
                    if qnow in ferteis: break
                    pass
                pass
            pass
        return ferteis
    
    def get_alcancaveis(self): # const
        '''
        Obtém-se os estados alcançáveis deste AF
        @return: Um conjunto contendo os estados alcançáveis
        @rtype: set
        '''
        alcancaveis = set([self.S])
        falta = [self.S]
        while falta:
            qnow = falta.pop()
            for t in self.alfabeto():
                for qnext in self.get_pos_as_set(qnow, t):
                    if qnext not in alcancaveis:
                        alcancaveis.add(qnext)
                        falta.append(qnext)
                        pass
                    pass
                pass
            pass
        return alcancaveis
    
    def eliminar_inuteis(self):
        '''
        Elimina os estados inúteis deste AF (modifica o objeto self)
        @return: Retorna este AF sem estados inúteis
        @rtype: AF
        '''
        ferteis = self.get_ferteis()
        if self.S not in ferteis:
            self.S = None
            self.tabela = {}
            self.finais = set([])
            return self
        for qnow in self.get_estados():
            if qnow not in ferteis:
                del self.tabela[qnow]
                continue
            else:
                for t in self.alfabeto():
                    qnextset = self.get_pos_as_set(qnow, t)
                    newqnextset = set([])
                    for qnext in qnextset:
                        if qnext in ferteis:
                            newqnextset.add(qnext)
                            pass
                        pass
                    self.tabela[qnow][t] = newqnextset
                    pass
                pass
            pass
        alcancaveis = self.get_alcancaveis()
        for qnow in self.get_estados():
            if qnow not in alcancaveis:
                del self.tabela[qnow]
                self.finais.discard(qnow)
            pass
        return self
    
    def minimizar(self):
        '''
        Responsável por minimizar este AF (self)
        Este AF deve ser deterministico
        Elimina os estados inúteis deste AF (modifica o objeto self)
        Minimiza este AF
        @return: Um novo AF equivalente a este (self), e minimizado
        @rtype: AF
        @raise None: caso o AF seja não-deterministico
        '''
        if not self.is_deterministico(): raise None
        self.eliminar_inuteis()
        nao_finais = set(self.get_estados()).difference(self.finais)
        nao_finais.add('') # qerro
        CElist = []
        if nao_finais: CElist.append(nao_finais) # if not empty
        if self.finais: CElist.append(set(self.finais)) # if not empty
        lenCElist = 0
        while lenCElist != len(CElist):
            lenCElist = len(CElist)
            newCElist = []
            for CE in CElist:
                newCE = set([])
                qrepr = CE.pop() # representante
                CE.add(qrepr)
                for t in self.alfabeto():
                    try:qreprnext = self.get_pos_as_set(qrepr, t).pop()# AFD -> len == 1
                    except:qreprnext = ''
                    for q in CE:
                        try:qnext = self.get_pos_as_set(q, t).pop()# AFD -> len == 1
                        except:qnext = ''
                        for C in CElist:
                            if xor(qnext in C, qreprnext in C):
                                newCE.add(q)
                                break
                            pass
                        pass
                    pass
                newCElist.append(CE.difference(newCE))
                if newCE: newCElist.append(newCE) # if is not empty
                pass
            CElist = newCElist
            pass
        M = AF()
        for CEnowi in range(len(CElist)):
            CE = CElist[CEnowi]
            CEnow = AF.get_nth_name(CEnowi)
            M.tabela[CEnow] = {}
            if self.S in CE: M.S = CEnow
            if CE.intersection(self.finais): # if is not empty
                M.finais.add(CEnow)
                pass
            q = CE.pop()
            CE.add(q)
            for t in self.alfabeto():
                try:qnext = self.get_pos_as_set(q, t).pop()# len == 1
                except:qnext = ''
                for CEnexti in range(len(CElist)):
                    if qnext in CElist[CEnexti]:
                        M.tabela[CEnow][t] = AF.get_nth_name(CEnexti)
                        break
                    pass
                pass
            pass
        return M
    
    def uniao(self, M1): # const
        '''
        Realiza a união deste AF (self) com M1
        @param M1: AF com o qual será realizado a união
        @type M1: AF
        @return: Um novo AF equivalente a união deste AF (self) com M1
        @rtype: AF
        '''
        M2 = AF()
        M2.S = 'S'
        M2.tabela['S'] = {}
        for k,Maq in {'A':self, 'B':M1}.items():
            if Maq.S in Maq.finais: M2.finais.add(M2.S)
            for f in Maq.finais: M2.finais.add(k+f)
            for t in Maq.alfabeto():
                try: M2.tabela['S'][t]
                except: M2.tabela['S'][t] = set([])
                for qnext in Maq.get_pos_as_set(Maq.S, t):
                    M2.tabela['S'][t].add(k+qnext)
                    pass
                pass
            for q in Maq.get_estados():
                M2.tabela[k+q] = {}
                for t in Maq.alfabeto():
                    M2.tabela[k+q][t] = set([])
                    for qnext in Maq.get_pos_as_set(q, t):
                        M2.tabela[k+q][t].add(k+qnext)
                        pass
                    pass
                pass
            pass
        return M2
    
    def complemento(self): # const
        '''
        Realiza o complemento deste AF (self)
        Este AF deve ser deterministico
        @return: Um novo AF equivalente ao complemente deste AF (self)
        @rtype: AF
        @raise None: Caso este AF seja não-deterministico
        '''
        if not self.is_deterministico(): raise None
        criar_qerro = False
        M = AF()
        if self.S is None:
            M.S = 'ERRO'
            criar_qerro = True
        else: M.S = 'C'+self.S
        for q in self.get_estados():
            M.tabela['C'+q] = {}
            if q not in self.finais: M.finais.add('C'+q)
            for t in self.alfabeto():
                M.tabela['C'+q][t] = set([])
                for qnext in self.get_pos_as_set(q, t):
                    M.tabela['C'+q][t].add('C'+qnext)
                    pass
                if not M.tabela['C'+q][t]: # if empty
                    M.tabela['C'+q][t].add('ERRO')
                    criar_qerro = True
                    pass
                pass
            pass
        if criar_qerro:
            M.tabela['ERRO'] = {}
            M.finais.add('ERRO')
            for t in self.alfabeto():
                M.tabela['ERRO'][t] = 'ERRO'
                pass
            pass
        return M
    
    pass
