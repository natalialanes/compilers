import yaml

from symtable import add_symbol, get_symbol

from ply import yacc

from logo_lexer import lexer, tokens

from tree import new_leaf, new_node, append_node


def p_program(prod):
    """program : expression other_expression"""
    node = new_node("program")
    append_node(node, prod[1])
    if prod[2]:
        append_node(node, prod[2])
    prod[0] = node


def p_another_statement(prod):
    """
    other_expression : expression other_expression
        | empty
    """
    if prod[1]:
        node = new_node("other_expression")
        append_node(node, prod[1])
        if prod[2]:
            append_node(node, prod[2])
        prod[0] = node


def p_expr(prod):
    """
    expression : value_expr
        | logo_expr
        | if_stmt
        | loop_stmt
        | assign_expr
        | params
    """
    node = new_node("expression")
    append_node(node, prod[1])
    prod[0] = node


def p_empty(prod):
    """empty :"""
    prod[0] = None


def p_func(prod):
    """logo_expr : PENUP
        | PU
        | PENDOWN
        | PD
        | WIPECLEAN
        | WC
        | CLEARSCREEN
        | CS
        | HOME
        | XCOR
        | YCOR
        | HEADING
        | RANDOM
        | TYPEIN
    """
    node = new_node("logo_function")
    append_node(node, new_leaf(prod.slice[1].type, value=prod[1]))


def p_only_param_func(prod):
    """logo_expr : FORWARD value_expr
        | FO value_expr 
        | BK value_expr 
        | BACKWARD value_expr
        | RIGHT value_expr
        | RT value_expr
        | LEFT value_expr
        | LT value_expr
        | PRINT value_expr
    """
    node = new_node("logo_function")
    append_node(node, new_leaf(prod.slice[1].type, value=prod[1]))
    append_node(node, prod[2])

    prod[0] = node


def p_two_params_func(prod):
    """logo_expr : SETXY value_expr value_expr"""
    node = new_node("logo_function")
    append_node(node, new_leaf(prod.slice[1].type, value=prod[1]))
    append_node(node, prod[2])
    append_node(node, prod[3])

    prod[0] = node


def p_value_expr_num(prod):  # noqa: D205, D400, D403, D415
    """value_expr : NUMBER"""
    node = new_node("value_expr")
    leaf = new_leaf("NUM", value=prod[1])
    append_node(node, leaf)
    prod[0] = node


def p_loop(prod):
    '''
        loop_stmt : WHILE bool_expr THEN expression END
    '''
    node = new_node('loop_stmt')
    append_node(node, 'WHILE')
    append_node(node, new_leaf('bool_expr', value=prod[2]))
    append_node(node, 'THEN')
    append_node(node, prod[4])
    append_node(node, 'END')
    prod[0] = node


def p_and_or(prod):
    """bool_expr_operator : AND 
        | OR
    """
    prod[0] = prod[1]


def p_if(prod):
    '''
        if_stmt : IF bool_expr THEN expression END
    '''
    node = new_node('if_stmt')
    append_node(node, 'IF')
    append_node(node, new_leaf('bool_expr', value=prod[2]))
    append_node(node, 'THEN')
    append_node(node, prod[4])
    append_node(node, 'END')
    prod[0] = node


def p_if_else(prod):
    '''
        if_stmt : IF bool_expr THEN expression ELSE expression END
    '''
    node = new_node('if_stmt')
    append_node(node, 'IF')
    append_node(node, new_leaf('bool_expr', value=prod[2]))
    append_node(node, 'THEN')
    append_node(node, prod[4])
    append_node(node, 'ELSE')
    append_node(node, prod[6])
    append_node(node, 'END')
    prod[0] = node


def p_boolean_expr(prod):
    '''
    bool_expr : value_expr EQUALS value_expr
        | value_expr GREATER value_expr
        | value_expr LOWER value_expr
        | value_expr GREATEQ value_expr
        | value_expr LOWEQ value_expr
    '''
    node = new_node('bool_expr')
    append_node(node, new_leaf(prod.slice[1].type, value=prod[1]))
    append_node(node, new_leaf(prod.slice[2].type, value=prod[2]))
    append_node(node, new_leaf(prod.slice[3].type, value=prod[3]))
    prod[0] = node


def p_one_more_bool_expr(prod):
    '''
        bool_expr : bool_expr bool_expr_operator bool_expr
    '''
    node = new_node('bool_expr')
    append_node(node, new_leaf(prod.slice[1].type, value=prod[1]))
    append_node(node, new_leaf(prod.slice[2].type, value=prod[2]))
    append_node(node, new_leaf(prod.slice[3].type, value=prod[3]))
    prod[0] = node


def p_assign(prod):
    '''assign_expr : TO IDENTIFIER params expression END'''
    node = new_node('assign_expr')
    append_node(node, new_leaf(prod.slice[1].type, value=prod[1]))
    append_node(node, new_leaf(prod.slice[2].type, value=prod[2]))
    append_node(node, new_leaf(prod.slice[3].type, value=prod[3]))
    append_node(node, new_leaf(prod.slice[4].type, value=prod[4]))
    append_node(node, new_leaf(prod.slice[5].type, value=prod[5]))
    prod[0] = node


def p_param(prod):
    '''params : ARGUMENT
        | params ARGUMENT'''
    node = new_node('arguments')
    try:
        append_node(node, prod[1])
        append_node(node, prod[2])
    except:
        pass
    prod[0] = node


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
            FORWARD 30 
        END
        WHILE 3 > 2 THEN FORWARD 20 END
        IF 20 > 4 AND 90 > 30 THEN 
            FORWARD 20
        END
        IF 2 > 1 AND 10 > 2 THEN 
            FORWARD 30
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
    print(yaml.dump(program, indent=2, sort_keys=False))

