#coding: utf-8
'''
Created on 15/06/2017

@author: cesar
'''

letrasmin = [chr(c) for c in range(ord('a'),ord('z')+1)]
letrasmai = [chr(c) for c in range(ord('A'),ord('Z')+1)]
digitos = [str(i) for i in range(10)]

class DeSimone(object):
    '''
    Classe responsável por manter as funções referentes a DeSimone
    '''
    
    @staticmethod
    def DeSimone(ER):
        '''
        Responsável por criar uma tabela AF para uma dada ER
        @param ER: Expressão regular
        @type ER: str
        @return: tabela de transições do AF representante da ER
        @rtype: dict
        '''
        ER = ER.replace(" ", "")
        arveres = DeSimone.criar_arvore(DeSimone.organizar_ER(ER))
        composicao = arveres.desce()
        composicoes = [composicao]
        q0 = {"composicao": composicao}
        AF = {0: q0}
        falta = [q0]
        while(falta):
            oi = falta.pop(0)
            for folha in oi["composicao"]:
                if folha is None: continue
                terminal = folha._me
                if(terminal not in oi.keys()): oi[terminal] = set([])
                oi[terminal] = oi[terminal].union(folha.sobe())
                pass
            for terminal in oi.keys():
                if terminal == "composicao": continue
                composicao = oi[terminal]
                if composicao not in composicoes:
                    composicoes.append(composicao)
                    q = {"composicao": composicao}
                    AF[composicoes.index(composicao)] = q
                    falta.append(q)
                    pass
                oi[terminal] = composicoes.index(composicao)
                pass
            pass
        return AF
        pass
    pass

    @staticmethod
    def organizar_ER(ER):
        '''
        Responsável por organizar uma string de ER em listas de listas.
        Cada lista referente a uma operação (concatenação, união, fecho, ...)
        @param ER: Expressão regular
        @type ER: str
        @return: ER organizada em listas de listas
        @rtype: list
        '''
        concatena = []
        uniao = []
        parenteses = []
        for letra in ER:
            if(letra in ("*","?","+")):
                filho = concatena.pop()
                while len(filho) == 1 and not isinstance(filho, str):
                    filho = filho[0]
                if(filho[0] in ("*","?","+")):
                    if letra == filho[0]: tmp = filho
                    else: tmp = ("*", filho[1])
                else: tmp = (letra, filho)
                concatena.append(tmp)
                pass
            elif(letra == "("):
                tmp = (uniao, concatena)
                parenteses.append(tmp)
                uniao = []
                concatena = []
                pass
            elif(letra == ")"):
                for termo in uniao:
                    concatena = ("|",termo,concatena)
                    pass
                uniao, tmp = parenteses.pop() # throw error if empty 
                tmp.append(concatena)
                concatena = tmp
                pass
            elif(letra == "|"):
                uniao.append(concatena)
                concatena = []
                pass
            elif(letra in letrasmin
                 or letra in digitos):
                concatena.append(letra)
                pass
            else: raise None # throw error if is not valid
            pass
        if parenteses: raise None # throw error if not empty
        for termo in uniao:
            concatena = ("|",termo,concatena)
            pass
        return concatena
    
    @staticmethod
    def criar_arvore(ER_list):
        '''
        Responsável por criar a árvore de DeSimone de uma ER regular já organizada em listas de listas
        @param ER_list: Listas de listas contendo a ER organizada por 'DeSimone.organizar_ER'
        @type ER_list: list
        @return: a árvore de DeSimone
        @rtype: Arvore
        '''
        if(len(ER_list) == 1):
            ER_list = ER_list[0]
            if(len(ER_list) == 1): return Arvore(ER_list)
            return DeSimone.criar_arvore(ER_list)
        elif(ER_list[0] in ("*","?","+")):
            assert len(ER_list)==2
            arvere = DeSimone.criar_arvore(ER_list[1])
            if(ER_list[0] == "+"):     return FechoPos(arvere)
            elif(ER_list[0] == "*"):   return Fecho(arvere)
            elif(ER_list[0] == "?"):   return Duvida(arvere)
        elif(ER_list[0] == "|"):
            assert len(ER_list)==3
            arvereL = DeSimone.criar_arvore(ER_list[1])
            arvereR = DeSimone.criar_arvore(ER_list[2])
            return Uniao(arvereL, arvereR)
        else:
            arvereL = DeSimone.criar_arvore(ER_list.pop(0))
            for termo in ER_list:
                arvereR = DeSimone.criar_arvore(termo)
                arvereL = Concatena(arvereL, arvereR)
            pass
            return arvereL
        pass
    
    pass


class Arvore(object):
    '''
    Nodo de árvore de DeSimone.
    Responsável por manter um terminal do alfabeto (caso não seja terminal, deverá usar suas subclasses)
    '''
    _me = None
    _daddy = None

    def __init__(self, letra):
        '''
        Construtor de um nodo folha da árvore de DeSimone
        @param letra: terminal representado por este nodo
        @type letra: str
        '''
        self._me = letra[0]
        pass
    
    def setDaddy(self, node):
        '''
        Define o nodo pai deste nodo (self)
        @param node: nodo pai
        @type node: subclasses de Arvore
        '''
        self._daddy = node
        pass
    
    def sobe(self):
        '''
        Operação sobe de DeSimone.
        Mantém a referência a um nodoloop
        Enquanto tal nodo não for o filho esquerdo do pai, pega-se o pai como atual nodoloop
        Ao encontrar o pai que tem como filho esquerdo o nodoloop, retorna a operação sobe do pai
        Caso não encontre (alcançou a raiz), será retornado um conjunto contendo None (representando lambda) 
        @return: Um conjunto contendo os nodos alcançados pela operação sobe deste nodo
        @rtype: set
        '''
        some1 = self
        daddy = some1._daddy
        while(daddy is not None and
              some1 != daddy._lson):
            some1 = daddy
            daddy = some1._daddy
            pass
        if(daddy is None): return set([None]) #lambda
        return daddy.sobe()
    
    def desce(self):
        '''
        Operação desce de DeSimone.
        Como esta classe representa um nodo folha, será retornado este objeto
        @return: Conjunto contendo este objeto (self)
        @rtype: set
        '''
        return set([self])
    
    pass

class Concatena(Arvore):
    '''
    Subclasse de Arvore
    Nodo de DeSimone responsável pela concatenação
    '''
    _me = "."

    def __init__(self, arvereL, arvereR):
        '''
        Construtor de um nodo de concatenação da árvore de DeSimone
        @param arvereL: Filho esquerdo deste nodo
        @type arvereL: Arvore
        @param arvereR: Filho direito deste nodo
        @type arvereR: Arvore
        '''
        self._lson = arvereL
        self._lson.setDaddy(self)
        self._rson = arvereR
        self._rson.setDaddy(self)
        pass
    
    def sobe(self):
        '''
        Operação sobe de DeSimone.
        Chama a operação desce do filho direito
        @return: O retorno da operação 'desce' do filho direito
        @rtype: set
        '''
        return self._rson.desce()
    
    def desce(self):
        '''
        Operação desce de DeSimone.
        Chama a operação desce do filho esquerdo
        @return: O retorno da operação 'desce' do filho esquerdo
        @rtype: set
        '''
        return self._lson.desce()
    
    pass

class Uniao(Arvore):
    '''
    Subclasse de Arvore
    Nodo de DeSimone responsável pela união
    '''
    _me = "|"

    def __init__(self, arvereL, arvereR):
        '''
        Construtor de um nodo de união da árvore de DeSimone
        @param arvereL: Filho esquerdo deste nodo
        @type arvereL: Arvore
        @param arvereR: Filho direito deste nodo
        @type arvereR: Arvore
        '''
        self._lson = arvereL
        self._lson.setDaddy(self)
        self._rson = arvereR
        self._rson.setDaddy(self)
        pass
    
    def sobe(self):
        '''
        Operação sobe de DeSimone.
        Chama a operação sobe da Arvore (superclasse)
        @return: O retorno da operação 'sobe' da Arvore (superclasse)
        @rtype: set
        '''
        return Arvore.sobe(self)
    
    def desce(self):
        '''
        Operação desce de DeSimone.
        Chama a operação desce do filho direito, e do filho esquerdo
        @return: A união dos retornos da operação 'desce' dos filhos esquerdo e direito
        @rtype: set
        '''
        result = self._lson.desce()
        return result.union(self._rson.desce())
    
    pass

class Fecho(Arvore):
    '''
    Subclasse de Arvore
    Nodo de DeSimone responsável pelo fecho
    '''
    _me = "*"

    def __init__(self, arvereL):
        '''
        Construtor de um nodo de fecho da árvore de DeSimone
        @param arvereL: Filho esquerdo deste nodo
        @type arvereL: Arvore
        '''
        self._lson = arvereL
        self._lson.setDaddy(self)
        pass
    
    def desce(self):
        '''
        Operação desce de DeSimone.
        Chama a operação desce do filho esquerdo, e a operação sobe da Arvore (superclasse)
        @return: A união dos retornos da operação 'desce' do filho esquerdo com a operação sobe da Arvore (superclasse)
        @rtype: set
        '''
        result = self._lson.desce()
        return result.union(Arvore.sobe(self))
    
    def sobe(self):
        '''
        Operação sobe de DeSimone.
        Igual a operação desce (chama a operação desce) 
        @return: O retorno da operação 'desce'
        @rtype: set
        '''
        return Fecho.desce(self)
    
    pass

class FechoPos(Fecho):
    '''
    Subclasse de Fecho
    Nodo de DeSimone responsável pelo fecho positivo
    '''
    _me = "+"

    def __init__(self, arvereL):
        '''
        Construtor de um nodo de fecho positivo da árvore de DeSimone
        @param arvereL: Filho esquerdo deste nodo
        @type arvereL: Arvore
        '''
        self._lson = arvereL
        self._lson.setDaddy(self)
        pass
    
    def desce(self):
        '''
        Operação desce.
        Diferente do Fecho, chama apenas a operação desce do filho esquerdo
        @return: O retorno da operação 'desce' do filho esquerdo
        @rtype: set
        '''
        return self._lson.desce()
    
    pass

class Duvida(Fecho):
    '''
    Subclasse de Fecho
    Nodo de DeSimone responsável pela dúvida (?)
    '''
    _me = "?"

    def __init__(self, arvereL):
        '''
        Construtor de um nodo de dúvida (?) da árvore de DeSimone
        @param arvereL: Filho esquerdo deste nodo
        @type arvereL: Arvore
        '''
        self._lson = arvereL
        self._lson.setDaddy(self)
        pass
    
    def sobe(self):
        '''
        Operação sobe de DeSimone.
        Diferente do Fecho, chama apenas a operação sobe da Arvore (superclasse)
        @return: O retorno da operação sobe da Arvore (superclasse)
        @rtype: set
        '''
        return Arvore.sobe(self)
    
    pass
