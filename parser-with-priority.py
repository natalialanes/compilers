"""Implement a simple expression evaluator parses."""

# For easier connection with class examples, we use names such as E or T_prime.
# pylint: disable=invalid-name

# Language definition:
#
# S = A | E
# A = id = E
# E = TE'
# E' = +TE' | - TE' | &
# T = PT'
# T' = * PT' | / PT' | &
# P = FP'
# P' = ^ FP' | &
# F = ( E ) | num | idF'
# F' = (E) | &
# num = [+-]?([0-9]+(.[0-9]+)?|.[0-9]+)(e[0-9]+)+)?)

import math
import re


class Symbol:
    def __init__(self, value, type, line=None):
        self.value = value
        self.type = type
        self.line = line


class ParserError(Exception):
    """An error exception for parser errors."""


class Lexer:
    """Implements the expression lexer."""

    OPEN_PAR = 1
    CLOSE_PAR = 2
    OPERATOR = 3
    NUM = 4
    FUNC = 5
    IDENTIFIER = 6
    ASSIGNMENT = 7

    def __init__(self, data):
        """Initialize object."""
        self.data = data
        self.current = 0
        self.previous = -1
        self.num_re = re.compile(r"[+-]?(\d+(\.\d*)?|\.\d+)(e\d+)?")
        self.id_re = re.compile(r"[a-zA-Z][a-zA-Z]*")

    def __iter__(self):
        """Start the lexer iterator."""
        self.current = 0
        return self

    def error(self, msg=None):
        """Generate a Lexical Errro."""
        err = (
            f"Error at pos {self.current}: "
            f"{self.data[self.current - 1:self.current + 10]}"
        )
        if msg is not None:
            err = f"{msg}\n{err}"
        raise ParserError(err)

    def put_back(self):
        # At most une token can be put back in the stream.
        self.current = self.previous

    def get_char(self, current):
        try:
            return self.data[current]
        except Exception:
            return ''

    def peek(self):
        if self.current < len(self.data):
            current = self.current
            while self.data[current] in " \t\n\r":
                current += 1
            previous = current
            char = self.data[current]
            current += 1
            if char == "(":
                return Lexer.OPEN_PAR, char, current
            if char == ")":
                return Lexer.CLOSE_PAR, char, current
            # Do not handle minus operator.
            if char in "+/*^":
                return Lexer.OPERATOR, char, current
            if char == "=":
                return Lexer.ASSIGNMENT, char, current
            
            if self.id_re.match(char):
                char_concat = char
                char = self.get_char(current)
                while self.id_re.match(char):                    
                    char_concat += char
                    current += 1
                    char = self.get_char(current)
                    
                try:
                    symbol = symbol_table[char_concat]

                    if symbol.type == Lexer.IDENTIFIER:
                        return symbol.type, char_concat, current

                    return symbol.type, symbol.value, current
                        
                except Exception:
                    new_symbol = Symbol(None, Lexer.IDENTIFIER)
                    symbol_table[char_concat] = new_symbol
                    return new_symbol.type, char_concat, current
                #     raise Exception(
                #     f"Symbol not defined at {current}: "
                #     f"{self.data[current - 1:current + 10]}"
                # )
                    
            match = self.num_re.match(self.data[current - 1 :])
            if match is None:
                # If there is no match we may have a minus operator
                if char == "-":
                    return (Lexer.OPERATOR, char, current)
                # If we get here, there is an error an unexpected char.
                raise Exception(
                    f"Error at {current}: "
                    f"{self.data[current - 1:current + 10]}"
                )
            current += match.end() - 1
            return (Lexer.NUM, match.group().replace(" ", ""), current)
        return (None, None, self.current)

    def __next__(self):
        """Retrieve the next token."""
        token_id, token_value, current = self.peek()
        if token_id is not None:
            self.previous = self.current
            self.current = current
            return (token_id, token_value)
        raise StopIteration()


symbol_table = {
    "sin": Symbol(math.sin, Lexer.FUNC),
    "cos": Symbol(math.cos, Lexer.FUNC),
    "tan": Symbol(math.tan, Lexer.FUNC),
    "log": Symbol(math.log, Lexer.FUNC)
}


def parse_S(data):
    try:
        last_current = data.current
        token, value = next(data)
    except StopIteration:
        return False

    identifier = value

    if token not in [Lexer.IDENTIFIER]:
        data.current = last_current
        return parse_E(data)
    else:
        token, value = next(data)
        if value == '=':
            return parse_A(data, identifier)
        else:
            data.current = last_current
            return parse_E(data)


def parse_A(data, id_name):
    symbol_table[id_name] = Symbol(parse_E(data), Lexer.IDENTIFIER)
    return True


def parse_E(data):
    """Parse rule E."""
    # print("E -> TE'")
    # E -> TE'  { $0 = T + E' }
    T = parse_T(data)
    E_prime = parse_E_prime(data)
    return T + (E_prime or 0)


def parse_E_prime(data):
    """Parse rule E'."""
    # print("E' -> +TE' | -TE'| &")
    try:
        token, operator = next(data)
    except StopIteration:
        # E' -> &  { $0 = 0 }
        return 0
    if token == Lexer.OPERATOR and operator in "+-":
        # E' -> +TE' { $0 = T + E' } | -TE' { $0 = T - E' }
        T = parse_T(data)
        E_prime = parse_E_prime(data)
        return (T if operator == "+" else -1 * T) + (E_prime or 0)

    if token not in [Lexer.OPERATOR, Lexer.OPEN_PAR, Lexer.CLOSE_PAR]:
        data.error(f"Invalid character: {operator}")

    # E' -> &  { $0 = 0 }
    data.put_back()
    return 0


def parse_T(data):
    """Parse rule T."""
    # print("T -> FT'")
    # T -> FT'  { $0 = F * T' }
    P = parse_P(data)
    T_prime = parse_T_prime(data)
    return P * (T_prime or 1)


def parse_T_prime(data):
    """Parse rule T'."""
    # print("T' -> *FT' | /FT'| &")
    try:
        token, operator = next(data)
    except StopIteration:
        # T' -> &  { $0 = 1 }
        return 1
    if token == Lexer.OPERATOR and operator in "*/":
        # T' -> *FT' { $0 = F*T' } | /FT' {$0 = F*(1/T')}
        P = parse_P(data)
        T_prime = parse_T_prime(data)
        return (P if operator == "*" else 1 / P) * T_prime

    if token not in [Lexer.OPERATOR, Lexer.OPEN_PAR, Lexer.CLOSE_PAR]:
        data.error(f"Invalid character: {operator}")

    # T' -> &  { $0 = 1 }
    data.put_back()
    return 1


def parse_P(data):
    F = parse_F(data)
    P_prime = parse_P_prime(data)
    return math.pow(F, P_prime)


def parse_P_prime(data):
    try:
        token, operator = next(data)
    except StopIteration:
        return 1
    if token == Lexer.OPERATOR and operator in "^":
        F = parse_F(data)
        P_prime = parse_P_prime(data)
        return math.pow(F, P_prime)
    
    if token not in [Lexer.OPERATOR, Lexer.OPEN_PAR, Lexer.CLOSE_PAR]:
        data.error(f"Invalid character: {operator}")

    data.put_back()
    return 1


def parse_F(data):
    """Parse rule F."""
    # print("F -> num | (E)")
    try:
        last_current = data.current
        token, value = next(data)
    except StopIteration:
        raise Exception("Unexpected end of source.") from None
    if token == Lexer.OPEN_PAR:
        # F -> (E)  { $0 = E }
        E = parse_E(data)
        try:
            if next(data) != (Lexer.CLOSE_PAR, ")"):
                data.error("Unbalanced parenthesis.")
        except StopIteration:
            data.error("Unbalanced parenthesis.")
        return E
    if token == Lexer.NUM:
        # F -> num   { $0 = float(num) }
        return float(value)
    if token == Lexer.IDENTIFIER:
        data.current = last_current
    if token == Lexer.FUNC or Lexer.IDENTIFIER:
        F_PRIME = parse_F_prime(data)
        if token == Lexer.FUNC:
            return value(F_PRIME)
        else:
            return F_PRIME
    raise data.error(f"Unexpected token: {value}.")


def parse_F_prime(data):
    try:
        token, value = next(data)
    except StopIteration:
        return 1
    if token == Lexer.OPEN_PAR:
        # F -> (E)  { $0 = E }
        E = parse_E(data)
        try:
            if next(data) != (Lexer.CLOSE_PAR, ")"):
                data.error("Unbalanced parenthesis.")
        except StopIteration:
            data.error("Unbalanced parenthesis.")
        return E
    if token == Lexer.IDENTIFIER:
        return symbol_table[value].value
    
    if token not in [Lexer.OPEN_PAR]:
        data.error(f"Invalid character: {value}")

    data.put_back()
    return 1


def parse(source_code):
    """Parse the source code."""
    lexer = Lexer(source_code)
    return parse_S(lexer)


if __name__ == "__main__":
    expressions = [
        ("a = 2", True),
        ("a * a", 2 * 2),
        ("5 / 4", 5 / 4),
        ("2 * 3 + 1", 2 * 3 + 1),
        ("1 + 2 * 3", 1 + 2 * 3),
        ("(2 * 3) + 1", (2 * 3) + 1),
        ("2 * (3 + 1)", 2 * (3 + 1)),
        ("(2 + 1) * 3", (2 + 1) * 3),
        ("-2 + 3", -2 + 3),
        ("5 + (-2)", 5 + (-2)),
        ("5 * -2", 5 * -2),
        ("-1 - -2", -1 - -2),
        ("-1 - 2", -1 - 2),
        ("4 - 5", 4 - 5),
        ("1 - 2", 1 - 2),
        ("3 - ((8 + 3) * -2)", 3 - ((8 + 3) * -2)),
        ("2.01e2 - 200", 2.01e2 - 200),
        ("2*3*4", 2 * 3 * 4),
        ("2 + 3 + 4 * 3 * 2 * 2", 2 + 3 + 4 * 3 * 2 * 2),
        ("10 + 11", 10 + 11),
        ("2 ^ 3", math.pow(2, 3)),
        ("3 * 3 ^ 2" ,3 * math.pow(3, 2)),
        ("2 ^ 2 + 3", math.pow(2, 2) + 3),
        ("2 ^ (2 + 3)", math.pow(2, 5)),
        ("cos(10)", math.cos(10)),
        ("sin(20)", math.sin(20)),
        ("tan(30)", math.tan(30)),
        ("3 * cos(10)", 3* math.cos(10)),
        ("sin(20) + 15", math.sin(20) + 15),
        ("tan(30) + sin(20)", math.tan(30) + math.sin(20)),
        ("tan(sin(2^3)) + sin(20)", math.tan(math.sin(math.pow(2, 3))) + math.sin(20)),
        ("log(20) + 15", math.log(20) + 15),
        ("log(160)", math.log(160)),
        ("abc = log(160)", True),
        ("abc + 1", math.log(160) + 1),
        ("abc = abc + 1", True),
        ("abc * 2", (math.log(160) + 1) * 2),
        ("fun = log(200)", True),
        ("30 + fun", 30 + math.log(200))
    ]
    for expression, expected in expressions:
        result = "PASS" if parse(expression) == expected else "FAIL"
        print(f"Expression: {expression} - {result}")