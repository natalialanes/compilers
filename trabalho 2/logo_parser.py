from symtable import add_symbol, get_symbol

from ply import yacc

from logo_lexer import lexer, tokens


def p_program(prod):
    """program : expression other_expression"""
    add_symbol('angle', 'CONST', None, value=0)
    statements = [prod[1]]
    if prod[2]:
        statements.extend(prod[2])
    prod[0] = statements
    print("\n".join(str(s) for s in statements))


def p_another_statement(prod):
    """
    other_expression : expression other_expression
        | empty
    """
    if prod[1]:
        statements = [prod[1]]
        if prod[2]:
            statements.extend(prod[2])
        prod[0] = statements


def p_expr(prod):
    """
    expression : value_expr
        | logo_expr
        | if_stmt
        | loop_stmt
        | assign_expr
        | params
    """
    prod[0] = prod[1]


def p_empty(prod):
    """empty :"""
    prod[0] = None


def p_draw_segment(prod):
    """logo_expr : FORWARD value_expr
        | FO value_expr 
        | BK value_expr 
        | BACKWARD value_expr 
    """
    if prod[1] == 'FORWARD' or prod[1] == 'FO':
        prod[0] = f'Turtle.draw_segment(angle, {prod[2]})'
    elif prod[1] == 'BACKWARD' or prod[1] == 'BK':
        prod[0] = f'angle = angle + 180 | '
        prod[0] += f'if angle > 360 then angle = angle - 360 | '
        prod[0] += f'Turtle.draw_segment(angle, {prod[2]})'
    

def p_set_position(prod):
    """logo_expr : RIGHT value_expr 
        | RT value_expr
        | LEFT value_expr  
        | LT value_expr 
        | HOME
    """
    if prod[1] == 'RIGHT' or prod[1] == 'RT':
        prod[0] = f'angle = angle + {prod[2]} | '
        prod[0] += f'if angle > 360 then angle = angle - 360 | '
        prod[0] += f'Turtle.set_position(angle, 0)'
    elif prod[1] == 'LEFT' or prod[1] == 'LT':
        prod[0] = f'angle = angle + {prod[2]} | '
        prod[0] += f'if angle < 0 then angle = angle + 360 | '
        prod[0] += f'Turtle.set_position(angle, {prod[2]})'
    else:
        prod[0] = 'Turtle.set_position(angle, 0)'


def p_set_draw(prod):
    """logo_expr : PENUP
        | PU
        | PENDOWN
        | PD
    """
    value = prod[0] == 'PENDOWN' or prod[1] == 'PD'
    prod[0] = f'Turtle.set_draw({value})'


def p_screen(prod):
    """logo_expr : WIPECLEAN
        | WC
        | CLEARSCREEN
        | CS
    """
    prod[0] = 'Turtle.clear()'
    if prod[1] == 'CLEARSCREEN' or prod[1] == 'CS':
        prod[0] += ' | Turtle.set_position(0, 0)'
        prod[0] += ' | angle = 0'


def p_set_x_y(prod):
    """logo_expr : SETXY value_expr value_expr"""
    prod[0] = f'Turtle.set_position({prod[2]}, {prod[3]})'


def p_get_position(prod):
    """logo_expr : HEADING
        | XCOR
        | YCOR
    """
    if prod[1] == 'HEADING':
        prod[0] = 'Turtle.get_position()'
    elif prod[1] == 'XCOR':
        prod[0] = f'Turtle.get_x_position({prod[2]})'
    elif prod[1] == 'YCOR':
        prod[0] = f'Turtle.get_y_position({prod[2]})'


def p_random(prod):
    """value_expr : RANDOM"""
    prod[0] = 'Turtle.random()'


def p_value_expr_num(prod):  # noqa: D205, D400, D403, D415
    """value_expr : NUMBER"""
    prod[0] = prod[1]


def p_and_or(prod):
    """bool_expr_operator : AND 
        | OR
    """
    prod[0] = prod[1]


def p_if(prod):
    '''
        if_stmt : IF bool_expr THEN expression END
    '''
    prod[0] = f'IF {prod[2]} THEN {prod[4]} END'


def p_if_else(prod):
    '''
        if_stmt : IF bool_expr THEN expression ELSE expression END
    '''
    prod[0] = f'IF {prod[2]} THEN {prod[4]} ELSE {prod[6]} END'


def p_loop(prod):
    '''
        loop_stmt : WHILE bool_expr THEN expression END
    '''
    prod[0] = f'WHILE {prod[2]} THEN {prod[4]} END'


def p_bool_expr(prod):
    '''
    bool_expr : value_expr EQUALS value_expr
        | value_expr GREATER value_expr
        | value_expr LOWER value_expr
        | value_expr GREATEQ value_expr
        | value_expr LOWEQ value_expr
    '''
    prod[0] = f'{prod[1]} {prod[2]} {prod[3]}'


def p_one_more_bool_expr(prod):
    '''
        bool_expr : bool_expr bool_expr_operator bool_expr
    '''
    prod[0] = f'{prod[1]} {prod[2]} {prod[3]}'


def p_assign(prod):
    '''assign_expr : TO IDENTIFIER params expression END'''
    add_symbol(prod[2], 'FUNC', prod.lineno(2), value=prod[4])
    prod[0] = f'{prod[1]} {prod[2]} {prod[3]} {prod[4]} {prod[5]}'


def p_param(prod):
    '''params : ARGUMENT
        | params ARGUMENT'''
    try:
        prod[0] = f'{prod[1]} {prod[2]}'
    except:
        prod[0] = f'{prod[1]}'


def p_error(token):
    """Provide a simple error message."""
    if token:
        raise Exception(
            f"Unexpected token:{token.lineno}: {token.type}:'{token.value}'"
        )

    raise Exception("Syntax error at EOF.")


if __name__ == "__main__":
    SOURCE = '''
        TO ABC :TESTE :OUTROPARAM 
            FORWARD 10 
        END
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
    mylex = lexer()
    parser = yacc.yacc(start="program")
    program = parser.parse(SOURCE, lexer=mylex, tracking=False)

