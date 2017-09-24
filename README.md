# LFC.py
Trabalho de Linguagens Formais e Compiladores sobre Linguagens Regulares

# Manual do Usuário

## Janela principal

<img src=misc/mainwindow.png>

No topo há 2 botões:
* __Criar__: Abre uma janela de diálogo para a criação de novos AFs.
* __Deletar__: Deleta o atual AF (o qual estará aparecendo na área centro-direita).

À esquerda há abas para a seleção de AFs. Na aba estará o nome do AF.
* __Manual__: aba referente a um Manual.
* __M1__: aba referente a um AF. M1 é o nome do AF.

Ao centro-direita, há 1 entrada de texto, 2 botões, e uma área para a Tabela de Transições:
* __Descrição__: Uma descrição do AF, meramente para informação (não é o nome do AF)(não afetará nenhuma operação). Pode ser editada.
* __Novo estado__: Cria uma nova linha na tabela de transições.
* __Novo terminal__: Cria uma nova coluna na tabela de transições.
* __Tabela de Transições__: Aqui ficará o AF representado como tabela de transições.

Na base há 6 botões, e 1 entrada de texto:
* __Determinizar__: Determiniza o atual AF.
* __Minimizar__: Minimiza o atual AF.
* __Complemento__: Realiza o complemento do atual AF.
* __União__: Realiza a união do atual AF com o AF representado na área “Operar com”.
* __Intersecção__: Realiza a intersecção do atual AF com o AF representado na área “Operar com”.
* __Diferença__: Realiza a diferença do atual AF com o AF representado na área “Operar com”.
* __Operar com__: Entrada para o nome do AF a ser realizado uma operação que envolva 2 AFs.

## Janela de Diálogo

<img src=misc/dialog.png>

Na janela de diálogo para a criação de AFs, há 1 entrada de texto, e 2 botões:
* __ER__: Entrada para uma expressão regular.
* __Criar AF da ER__: Criará um AF para a ER
* __Criar AF vazia__: Criará uma máquina de AF vazia.

## Observações

Nota: # = count → #"(" = count("(")

1. Para a ER, deve-se usar apenas:
    1. Letras minúsculas
    2. Dígitos
    3. Caracteres especiais de uma ER.
        1. São eles “(“, “)”, “+”, “?”, “*”, “|”
    4. Uma expressão regular bem formada
        1. #“(“ = #”)”, e bem formados (não fechar parênteses sem tê-lo aberto)
    5. Espaços podem ser usados (serão ignorados)
    6. & (épsilon) não é aceito
    0. → Caso não esteja nos conformes, o AF não será criado (carece de alertas no app)
2. Para a edição da Tabela de Transições deve-se:
    1. Nomear os estados com (uma série de) letras maiúsculas somente
        1. Caracteres que não estejam nos conformes serão ignorados.
        Ex: “[A,B]” será tratado como “AB”
            1. Cuidado com o perigo de nomear 2 linhas com o mesmo estado, incluindo a possibilidade dos estados “[AB,C]” e “[A,BC]” (ambos serão tratadas como “ABC”)
        2. “” (série vazia) representa indefinição
            1. Não tente usá-lo como estado válido (final ou não)
            2. Suas transições serão ignoradas (permanecerá na indefinição)
    2. Nomear os terminais com letras minúsculas e/ou dígitos somente
        1. Caracteres que não estejam nos conformes serão ignorados.
        Ex: “aS” será tratado como “a”
            1. Cuidado com o perigo de nomear 2 colunas com o mesmo terminal, incluindo a possibilidade dos terminais “aS” e “a” (ambos serão tratadas como “a”)
            2. Terminais que contenham mais de 1 símbolo válido resultarão num terminal de tamanho>1, e será ignorado.
            Ex: “aSb” será tratado como “ab”, o qual tem tamanho 2, e será ignorado
        2. & (épsilon) não é aceito (não há suporte para &-transições)
    3. Nomear as transições com (uma série de) letras maiúsculas e/ou vírgulas
        1. Em AFNDs, utilize vírgula para separar os estados
