'''
'''
from lexer import opening_delimiters, ending_delimiters, operator_delimiters, self_operator, number, is_string, is_variable
_operator_lookup = {':=':'03','+':'04','-':'05','*':'06','/':'07','//':'08','**':'09','%':'0a','<':'13','<=':'14','>':'15','>=':'16','=':'17','!=':'18',
                    '+:':'19','-:':'1a','*:':'1b','/:':'1c','//:':'1d','**:':'1e','%:':'1f'}
_tokens = []
_token_index = 0
_consts = [0]
_const_lookup = {0:0}
_var_lookup = {}
_func_data = []

def _peek(n = 1):
    return _tokens[_token_index + n-1] if _token_index + n-1 < len(_tokens) else None

def _next(n = 1):
    global _token_index
    token = _peek(n)
    _token_index += n
    return token

def copy_scope(scope):
    new_scope = {i: scope[i].copy() if hasattr(scope[i], 'copy') else scope[i] for i in scope}
    for child in range(len(new_scope["scopes"])):
        child_scope = copy_scope(new_scope["scopes"][child])
        child_scope["parent"] = new_scope
        new_scope["scopes"][child] = child_scope
    return new_scope

def _create_scope(parent = None, insert_code = False):
    if insert_code:
        return {"code": parent["code"], "goto": parent["goto"], "func": {}, "values": {}, "scopes": [], "parent": parent}
    else:
        return {"code": [], "goto": [], "func": {}, "values": {}, "scopes": [], "parent": parent}

def _add_var(var_name):
    if var_name not in _var_lookup:
        _var_lookup[var_name] = len(_var_lookup)

def _add_const(const):
    if const not in _const_lookup:
        _const_lookup[const] = len(_consts)
        _consts.append(const)

def _get_var(var_name):
    return '{:02x}'.format(_var_lookup[var_name])

def _eval(scope):
    token = _peek()
    if token in ending_delimiters:
        pass
    elif token == 'def':
        var_name = _next(2)
        _add_var(var_name)
        scope_defined = _peek() == '{'
        _add_var(var_name)
        if scope_defined:
            _next()
            _eval(scope)
            _next()
        scope_defined = '01' if scope_defined else '00'
        if _peek() == ':=':
            _next()
            _eval(scope)
            scope["code"].append('02' + _get_var(var_name) + scope_defined)
        elif _peek() == '(':
            _next()
            func_scope = _create_scope(scope)
            while _peek() != ')':
                arg_name = _next()
                _add_var(arg_name)
                func_scope["values"][int(_get_var(arg_name))] = None
                if _peek() == ',':
                    _next()
            _next(2)
            while _peek() != '}':
                _eval(func_scope)
                _next()
            scope["code"].append('22' + _get_var(var_name) + '{:02x}'.format(len(_func_data)) + scope_defined)
            _func_data.append(func_scope)
            _condense(func_scope)
        else:
            scope["code"].append('0b' + _get_var(var_name) + scope_defined)
    elif token == 'return':
        _next()
        if _peek() not in ending_delimiters:
            _eval(scope)
        else:
            scope["code"].append('00{:02x}'.format(0))
        scope["code"].append('0f')
    elif token == 'if':
        _next(2)
        _eval(scope)
        jump_else = len(scope["goto"])
        scope["goto"].append(None)
        if_scope = _create_scope(scope, True)
        scope["code"].append('10{:02x}'.format(jump_else))
        scope["code"].append('20{:02x}'.format(len(scope["scopes"])))
        scope["scopes"].append(if_scope)
        _next(2)
        while _peek() not in ending_delimiters:
            _eval(if_scope)
            _next()
        end_if = len(scope["code"])
        scope["code"].append(None)
        scope["goto"][jump_else] = len(scope["code"])
        if _peek(2) == 'else':
            _next(2)
            _eval(if_scope)
            _next()
        scope["code"][end_if] = '12{:02x}'.format(len(scope["goto"]))
        scope["goto"].append(len(scope["code"]))
    elif token == 'while':
        _next(2)
        repeat_while = len(scope["code"])
        _eval(scope)
        jump_while = len(scope["goto"])
        scope["goto"].append(None)
        while_scope = _create_scope(scope, True)
        scope["code"].append('10{:02x}'.format(jump_while))
        scope["code"].append('20{:02x}'.format(len(scope["scopes"])))
        scope["scopes"].append(while_scope)
        _next(2)
        while _peek() not in ending_delimiters:
            _eval(while_scope)
            _next()
        scope["code"].append('12{:02x}'.format(len(scope["goto"])))
        scope["goto"].append(repeat_while)
        scope["goto"][jump_while] = len(scope["code"])
    elif token == 'until':
        _next(2)
        repeat_until = len(scope["code"])
        _eval(scope)
        jump_until = len(scope["goto"])
        scope["goto"].append(None)
        until_scope = _create_scope(scope, True)
        scope["code"].append('11{:02x}'.format(jump_until))
        scope["code"].append('20{:02x}'.format(len(scope["scopes"])))
        scope["scopes"].append(until_scope)
        _next(2)
        while _peek() not in ending_delimiters:
            _eval(until_scope)
            _next()
        scope["code"].append('12{:02x}'.format(len(scope["goto"])))
        scope["goto"].append(repeat_until)
        scope["goto"][jump_until] = len(scope["code"])
    #manage other keywords here
    else:
        operators = []
        while _peek() not in ending_delimiters:
            token = _next()
            if number(token) is not None:
                token_value = number(token)
                _add_const(token_value)
                scope["code"].append('00{:02x}'.format(_const_lookup[token_value]))
            elif is_string(token):
                token = token[1:-1]
                _add_const(token)
                scope["code"].append('00{:02x}'.format(_const_lookup[token]))
            elif is_variable(token):
                scope_defined = _peek() == '{'
                if scope_defined:
                    _next()
                    _eval(scope)
                    _next()
                scope_defined = '01' if scope_defined else '00'
                if _peek() in opening_delimiters:
                    _next()
                    num_args = 0
                    while _peek() not in ending_delimiters:
                        _eval(scope)
                        num_args += 1
                        if _peek() == ',':
                            _next()
                    _next()
                    if token == 'print':
                        scope["code"].append('0d{:02x}'.format(num_args))
                    elif token == 'println':
                        scope["code"].append('0e{:02x}'.format(num_args))
                    else:
                        scope["code"].append('0c' + _get_var(token) + '{:02x}'.format(num_args) + scope_defined)
                elif _peek() in self_operator:
                    operator = _next()
                    _eval(scope)
                    scope["code"].append(_operator_lookup[operator] + _get_var(token) + scope_defined)
                else:
                    scope["code"].append('01' + _get_var(token) + scope_defined)
            elif token in opening_delimiters:
                _eval(scope)
                _next()
            else:
                while operators and operator_delimiters[token] >= operator_delimiters[operators[-1]]:
                    scope["code"].append(_operator_lookup[operators.pop()])
                operators.append(token)
        while operators:
            scope["code"].append(_operator_lookup[operators.pop()])

def _condense(scope):
    bytecode = ''
    code_start = [0]
    for num, command in enumerate(scope["code"]):
        code_start.append(len(bytecode + command) // 2 + 1)
        bytecode += '{:02x}'.format(code_start[-1]) + command
    for gotos in range(len(scope["goto"])):
        scope["goto"][gotos] = code_start[scope["goto"][gotos]]
    scope["code"] = bytecode

def parse(tokens):
    global _tokens
    _tokens = tokens
    bytecode = []
    scope = _create_scope()
    while _peek() is not None:
        _eval(scope)
        _next()
    _condense(scope)
    return scope
