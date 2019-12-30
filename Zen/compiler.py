import tokenizer
import tokens
import grammar
import scoping
import error

import collections

def _init(filename):
    global _get_tokens, _tokens
    global _var_lookup, _const_lookup, _func_lookup
    _get_tokens = tokenizer.tokenize(filename)
    _tokens = collections.deque()
    _var_lookup = {}
    _const_lookup = {0:0, 1:1}
    _func_lookup = []

def _peek(n = 1):
    try:
        while n > len(_tokens):
            _tokens.append(next(_get_tokens))
        return _tokens[n-1]
    except StopIteration:
        pass

def _next(n = 1):
    t = _peek(n)
    for i in range(n):
        if not _tokens:
            error.throw("Error: Unexpected EOF")
        _tokens.popleft()
    return t

def _add_var(var_name):
    if var_name not in _var_lookup:
        _var_lookup[var_name] = len(_var_lookup)

def _add_const(const):
    if const not in _const_lookup:
        _const_lookup[const] = len(_const_lookup)

def _get_var(var_name):
    _add_var(var_name)
    return '{:02x}'.format(_var_lookup[var_name])

def _condense(scope):
    bytecode = ''
    code_start = [0]
    for num, cmd in enumerate(scope["code"]):
        code_start.append(len(bytecode + cmd) // 2 + 1)
        bytecode += '{:02x}'.format(code_start[-1]) + cmd
    for goto in range(len(scope["goto"])):
        scope["goto"][goto] = code_start[scope["goto"][goto]]
    scope["code"] = bytecode

def _precedence(operator):
    for i, group in enumerate(grammar.OP_ORDER):
        if operator in group:
            return i

def _parse(scope):
    token = _peek()
    if token in grammar.END_DELIM:
        pass
    elif token in grammar.OPEN_DELIM:
        close = grammar.END_DELIM[grammar.OPEN_DELIM.index(_next())]
        while _peek() != close:
            _parse(scope)
            if close != _peek() in grammar.END_DELIM:
                _next()
        _next()
    elif token == 'def':
        var_name = _next(2)
        scope_def = _peek() == '{'
        _add_var(var_name)
        if scope_def:
            _parse(scope)
        scope_def = '01' if scope_def else '00'
        if _peek() == ':=':
            _next()
            _parse(scope)
            scope["code"].append('02' + _get_var(var_name) + scope_def)
        else:
            scope["code"].append('04' + _get_var(var_name) + scope_def)
    elif token == 'func':
        if _next(2) != '(':
            error.throw("Invalid Syntax")
        func_scope = scoping.scope(scope)
        while _peek() != ')':
            arg_name = _next()
            if _peek() == ':=':
                _next()
                arg_scope = scoping.scope(func_scope)
                eval(arg_scope)
            if _peek() == ',':
                _next()
            elif _peek() != ')':
                error.throw("Invalid Syntax")
        _next()
        _parse(func_scope)
        _condense(func_scope)
        scope["code"].append('22' + '{:02x}'.format(len(_func_lookup)))
        _func_lookup.append(func_scope)
    elif token == 'return':
        _next()
        if _peek() == ';':
            scope["code"].append('00{:02x}'.format(0))
        else:
            _parse(scope)
        scope["code"].append('0f')
    elif token == 'if':
        _next()
        if _peek() != '(':
            error.throw("Invalid Syntax")
        _parse(scope)
        jump_else = len(scope["goto"])
        if_scope = scoping.scope(scope, True)
        scope["goto"].append(None)
        scope["code"].append('10{:02x}'.format(jump_else))
        scope["code"].append('20{:02x}'.format(len(scope["scopes"])))
        scope["scopes"].append(if_scope)
        _parse(if_scope)
        end_if = len(scope["code"])
        scope["code"].append(None)
        scope["goto"][jump_else] = len(scope["code"])
        if _peek(2) == 'else':
            _next(2)
            _parse(scope)
        scope["code"][end_if] = '12{:02x}'.format(len(scope["goto"]))
        scope["goto"].append(len(scope["code"]))
    elif token == 'while':
        _next()
        if _peek() != '(':
            error.throw("Invalid Syntax")
        rep_while = len(scope["code"])
        _parse(scope)
        jump_while = len(scope["goto"])
        scope["goto"].append(None)
        while_scope = scoping.scope(scope, True)
        scope["code"].append('10{:02x}'.format(jump_while))
        scope["code"].append('20{:02x}'.format(len(scope["scopes"])))
        scope["scopes"].append(while_scope)
        _parse(while_scope)
        scope["code"].append('12{:02x}'.format(len(scope["goto"])))
        scope["goto"].append(rep_while)
        scope["goto"][jump_while] = len(scope["code"])
    elif token == 'until':
        _next()
        if _peek() != '(':
            error.throw("Invalid Syntax")
        rep_until = len(scope["code"])
        _parse(scope)
        jump_until = len(scope["goto"])
        scope["goto"].append(None)
        until_scope = scoping.scope(scope, True)
        scope["code"].append('11{:02x}'.format(jump_until))
        scope["code"].append('20{:02x}'.format(len(scope["scopes"])))
        scope["scopes"].append(until_scope)
        _parse(until_scope)
        scope["code"].append('12{:02x}'.format(len(scope["goto"])))
        scope["goto"].append(rep_until)
        scope["goto"][jump_until] = len(scope["code"])
    # manage other keywords here
    else:
        operators = []
        while _peek() not in grammar.END_DELIM:
            token = _next()
            if tokens.number(token) is not None:
                # replace with custom datatype
                value = tokens.number(token)
                _add_const(value)
                scope["code"].append('00{:02x}'.format(_const_lookup[value]))
            elif tokens.string(token):
                value = token[1:-1]
                _add_const(value)
                scope["code"].append('00{:02x}'.format(_const_lookup[value]))
            elif tokens.bool(token):
                value = token
                _add_const(value)
                scope["code"].append('00{:02x}'.format(_const_lookup[value]))
            elif tokens.variable(token):
                scope_def = _peek() == '{'
                if scope_def:
                    _parse(scope)
                scope_def = '01' if scope_def else '00'
                if _peek() == '(':
                    _next()
                    num_args = 0
                    while _peek() != ')':
                        _parse(scope)
                        num_args += 1
                        if _peek() == ',':
                            _next()
                    _next()
                    if token == 'print':
                        scope["code"].append('0d{:02x}'.format(num_args))
                    if token == 'println':
                        scope["code"].append('0e{:02x}'.format(num_args))
                    else:
                        scope["code"].append('0c' + _get_var(token) + '{:02x}'.format(num_args) + scope_def)
                elif _peek() in grammar.ASSIGN_OPS:
                    operator = _next()
                    _parse(scope)
                    scope["code"].append('{:02x}'.format(grammar.OP_LOOKUP[operator]) + _get_var(token) + scope_def)
                else:
                    scope["code"].append('01' + _get_var(token) + scope_def)
            else:
                while operators and _precedence(token) >= _precedence(operators[-1]):
                    scope["code"].append('{:02x}'.format(grammar.OP_LOOKUP[operators.pop()]))
                operators.append(token)
        while operators:
            scope["code"].append('{:02x}'.format(grammar.OP_LOOKUP[operators.pop()]))

def compile(filename):
    _init(filename)
    g_scope = scoping.scope()
    while _peek():
        _parse(g_scope)
        _next()
    _condense(g_scope)
    return g_scope
