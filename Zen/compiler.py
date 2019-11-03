'''
'''
from lexer import opening_delimiters, ending_delimiters, operator_delimiters, self_operator, number, is_string, is_variable
_operator_lookup = {':=':'03','+':'04','-':'05','*':'06','/':'07','//':'08','**':'09','%':'0a','<':'13','<=':'14','>':'15','>=':'16','=':'17','!=':'18',
                    '+:':'19','-:':'1a','*:':'1b','/:':'1c','//:':'1d','**:':'1e','%:':'1f'}
_tokens = []
_token_index = 0
_consts = []
_const_lookup = {}

def _peek(n = 1):
    return _tokens[_token_index + n-1] if _token_index + n-1 < len(_tokens) else None

def _next(n = 1):
    global _token_index
    token = _peek(n)
    _token_index += n
    return token

def copy_scope(scope):
    return {i: scope[i].copy() if hasattr(scope[i], 'copy') else scope[i] for i in scope}

def _create_scope():
    return {"vars": [], "var_lookup": {}, "funcs": [], "func_data": {}, "func_lookup": {}, "goto": [], "values": {}}

def _add_var(scope, var_name):
    if var_name not in scope["var_lookup"]:
        scope["var_lookup"][var_name] = len(scope["vars"])
        scope["vars"].append(var_name)

def _add_const(const):
    if const not in _const_lookup:
        _const_lookup[const] = len(_consts)
        _consts.append(const)

def _get_var(scope, var_name):
    scope_count = 0
    while "parent_scope" in scope and var_name not in scope["var_lookup"]:
        scope = scope["parent_scope"]
        scope_count += 1
    return '{0:02x}{1:02x}'.format(scope_count, scope["var_lookup"][var_name])

def _get_func(scope, func_name):
    scope_count = 0
    while "parent_scope" in scope and func_name not in scope["func_lookup"]:
        scope = scope["parent_scope"]
        scope_count += 1
    return '{0:02x}{1:02x}'.format(scope_count, scope["func_lookup"][func_name])

def _eval(bytecode, scope):
    token = _peek()
    if token in ending_delimiters:
        return bytecode
    elif token == 'def':
        var_name = _next(2)
        if _peek() == ':=':
            _next()
            _eval(bytecode, scope)
            _add_var(scope, var_name)
            bytecode.append('02' + _get_var(scope, var_name))
        elif _peek() == '(':
            _next()
            func_scope = _create_scope()
            func_scope["parent_scope"] = scope
            func_code = []
            while _peek() not in ending_delimiters:
                arg_name = _next()
                _add_var(func_scope, arg_name)
                if _peek() == ',':
                    _next()
            _next(2)
            if var_name not in scope["func_lookup"]:
                scope["func_lookup"][var_name] = len(scope["funcs"])
                scope["funcs"].append(var_name)
            while _peek() not in ending_delimiters:
                _eval(func_code, func_scope)
                _next()
            scope["func_data"][var_name] = (_condense(func_code, func_scope), func_scope)
        else:
            _add_var(scope, var_name)
            bytecode.append('0b' + _get_var(scope, var_name))
    elif token == 'return':
        _next()
        if _peek() not in ending_delimiters:
            _eval(bytecode, scope)
        else:
            _add_const(None)
            bytecode.append('00{:02x}'.format(_const_lookup[None]))
        bytecode.append('0f')
    elif token == 'if':
        _next(2)
        _eval(bytecode, scope)
        jump_else = len(scope["goto"])
        scope["goto"].append(None)
        bytecode.append('10{:02x}'.format(jump_else))
        _next(2)
        while _peek() not in ending_delimiters:
            _eval(bytecode, scope)
            _next()
        end_if = len(bytecode)
        bytecode.append(None)
        scope["goto"][jump_else] = len(bytecode)
        if _peek(2) == 'else':
            _next(2)
            _eval(bytecode, scope)
            _next()
        bytecode[end_if] = '12{:02x}'.format(len(scope["goto"]))
        scope["goto"].append(len(bytecode))
    elif token == 'while':
        _next(2)
        repeat_while = len(bytecode)
        _eval(bytecode, scope)
        jump_while = len(scope["goto"])
        scope["goto"].append(None)
        bytecode.append('10{:02x}'.format(jump_while))
        _next(2)
        while _peek() not in ending_delimiters:
            _eval(bytecode, scope)
            _next()
        bytecode.append('12{:02x}'.format(len(scope["goto"])))
        scope["goto"].append(repeat_while)
        scope["goto"][jump_while] = len(bytecode)
    elif token == 'until':
        _next(2)
        repeat_until = len(bytecode)
        _eval(bytecode, scope)
        jump_until = len(scope["goto"])
        scope["goto"].append(None)
        bytecode.append('11{:02x}'.format(jump_until))
        _next(2)
        while _peek() not in ending_delimiters:
            _eval(bytecode, scope)
            _next()
        bytecode.append('12{:02x}'.format(len(scope["goto"])))
        scope["goto"].append(repeat_until)
        scope["goto"][jump_until] = len(bytecode)
    else:
        operators = []
        while _peek() not in ending_delimiters:
            token = _next()
            if number(token) is not None:
                token_value = number(token)
                _add_const(token_value)
                bytecode.append('00{:02x}'.format(_const_lookup[token_value]))
            elif is_string(token):
                token = token[1:-1]
                _add_const(token)
                bytecode.append('00{:02x}'.format(_const_lookup[token]))
            elif is_variable(token):
                if _peek() in opening_delimiters:
                    _next()
                    num_args = 0
                    while _peek() not in ending_delimiters:
                        _eval(bytecode, scope)
                        num_args += 1
                        if _peek() == ',':
                            _next()
                    if token == 'print':
                        bytecode.append('0d{:02x}'.format(num_args))
                    elif token == 'println':
                        bytecode.append('0e{:02x}'.format(num_args))
                    else:
                        bytecode.append('0c' + _get_func(scope, token) + '{:02x}'.format(num_args))
                    _next()
                elif _peek() in self_operator:
                    operator = _next()
                    _eval(bytecode, scope)
                    bytecode.append(_operator_lookup[operator] + _get_var(scope, token))
                else:
                    bytecode.append('01' + _get_var(scope, token))
            elif token in opening_delimiters:
                _eval(bytecode, scope)
                _next()
            else:
                while operators and operator_delimiters[token] >= operator_delimiters[operators[-1]]:
                    bytecode.append(_operator_lookup[operators.pop()])
                operators.append(token)
        while operators:
            bytecode.append(_operator_lookup[operators.pop()])

def _condense(bytecode, scope):
    bytecode_string = ''
    bytecode_start = [0]
    for command_num, command in enumerate(bytecode):
        bytecode_start.append(len(bytecode_string + command) // 2 + 1)
        bytecode_string += '{:02x}'.format(bytecode_start[-1])
        bytecode_string += command
    for end_gotos in range(len(scope["goto"])):
        scope["goto"][end_gotos] = bytecode_start[scope["goto"][end_gotos]]
    return bytecode_string

def parse(tokens):
    global _tokens
    _tokens = tokens
    bytecode = []
    scope = _create_scope()
    while _peek() is not None:
        _eval(bytecode, scope)
        _next()
    return _condense(bytecode, scope), scope, _consts
