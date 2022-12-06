from ply import lex

symtable = {}

symtable_types = {'FUNC': 1, 'PARAM': 2}

logical = [
    "EQUALS",
    "GREATER",
    "LOWER",
    "GREATEQ",
    "LOWEQ",
]

reserved = [
    'FORWARD', 'FO', 'BACKWARD', 'BK', 'RIGHT', 'RT', 'LEFT', 'LT', 'PENUP', 'PU', 'PENDOWN', 
    'PD', 'WIPECLEAN', 'WC', 'CLEARSCREEN', 'CS', 'HOME', 'SETXY', 'XCOR', 'YCOR',
    'HEADING', 'RANDOM', 'IF', 'THEN', 'END', 'ELSE', 'WHILE', 'PRINT', 'TYPEIN', 'TO', "AND", "OR"
]

tokens = [
    'NUMBER', 'IDENTIFIER', 'ARGUMENT',
] + logical + reserved

t_EQUALS = '=='
t_GREATER = '>'
t_LOWER = '<'
t_GREATEQ = '>='
t_LOWEQ = '<='

t_ignore  = ' \t'

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_IDENTIFIER(t):
    r'[A-Z][A-Z]*'
    if t.value in (reserved or logical):
        t.type = t.value
    else:
        t.type = 'IDENTIFIER'

    if t.type == 'IDENTIFIER':
        try:
            symtable[t.value]
        except:
            symtable[t.value] = { symtable_types['FUNC'], None}
    return t

def t_ARGUMENT(t):
    r':[A-Z][A-Z]*'
    symtable[t.value] = { symtable_types['PARAM'], None }
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def lexer():
    """Create a new lexer object."""
    return lex.lex()

# Test it out
data = '''
    TO ABC :PARAM FORWARD 10 END
    WHILE 2 > 1 THEN FORWARD 10 END
    IF 10 > 5 AND 15 > 10 THEN 
        FORWARD 10
    END
    IF 10 > 5 AND 15 > 10 THEN 
        FORWARD 10
    ELSE
        FORWARD 20
    END
    CLEARSCREEN
    FORWARD 10
    BK 25
    RIGHT 30
    LEFT 20
    PENUP
    RANDOM
    SETXY 10 20
'''

# Give the lexer some input
the_lexer = lexer()
the_lexer.input(data)

for token in the_lexer:
    print(token)