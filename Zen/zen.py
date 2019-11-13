from sys import argv
import re
'''
Tokenizer
'''
_flags = {'-r':0,'-b':0,'-f':0,'-g':0}
_active_flags = set()
_raw_input = ''
_delimiters = {'!', '%', '^', '&', '*', '(', ')', '-', '+', ':=', '{', '}', '[', ']', '|', ';', ':', '<', '>', ',', '.', '?', '/',
               '&&', '||', '!=', '^=', '&=', '*:', '-:', '+:', '=', '|=', '<=', '>=', '/:', '//:' '++', '--', '**', '//'}
_ending = {')', '}', ']', ';', ','}
_opening = {'(', '{', '['}
_operators = {'%':1,'^':4,'&':3,'*':1,'-':2,'+':2,'|':5,'<':6,'>':6,'/':1,'&&':7,'||':8,'!=':6,'=':6,'<=':6,'>=':6,'**':0,'//':1,
                       ':=':7,'+:':7,'-:':7,'*:':7,'/:':7,'//:':7,'**:':7,'%:':7}
_self_operators = {':=', '+:', '-:', '*:', '/:', '//:', '**:', '%:'}
def _get_filename():
    filename = None
    if len(argv) > 1:
        arg = 1
        while arg < len(argv):
            if argv[arg] in _flags:
                arg += _flags[argv[arg]]
                _active_flags.add(argv[arg])
            elif not filename:
                filename = argv[arg]
            arg += 1
        return filename
    else:
        raise FileNotFoundError('File not specified')

def _read_file():
    filename = _get_filename()
    if filename[-3:] != '.zl':
        filename += '.zl'
    with open(filename, 'r') as f:
        return f.read()

def _check_prefix(token):
    prefixes = []
    for delimiter in _delimiters:
        if delimiter.startswith(token):
            prefixes.append(delimiter)
    return prefixes

def _is_number(token):
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return None

def _is_variable(token):
    return re.match('^[a-zA-Z_]\\w*$', token)

def _is_string(token):
    return token[0] == token[-1] and (token[0] == "'" or token[0] == '"')

def _is_bool(token):
    return token == 'true'

def _get_tokens():
    global _raw_input
    _raw_input = _read_file()
    tokens = []
    current_token = ''
    temporary_delimiter = ''
    flag_string = 0
    flag_escape = False
    for character in _raw_input:
        if character == '\\' and not flag_escape:
            flag_escape = True
            continue
        if flag_string == 1:
            current_token += character
            if character == '"' and not flag_escape:
                flag_string = 0
                tokens.append(current_token)
                current_token = ''
        elif flag_string  == 2:
            current_token += character
            if character == "'" and not flag_escape:
                flag_string = 0
                tokens.append(current_token)
                current_token = ''
        elif character.isspace():
            if current_token:
                tokens.append(current_token)
                current_token = ''
        elif character == '"' and not flag_escape:
            if current_token:
                tokens.append(current_token)
                current_token = ''
            if temporary_delimiter:
                tokens.append(temporary_delimiter)
                temporary_delimiter = ''
            current_token = character
            flag_string = 1
        elif character == "'" and not flag_escape:
            if current_token:
                tokens.append(current_token)
                current_token = ''
            if temporary_delimiter:
                tokens.append(temporary_delimiter)
                temporary_delimiter = ''
            current_token = character
            flag_string = 2
        elif character == '.' and _is_number(current_token + character) is not None:
            current_token += character
        elif character == '-' and not _check_prefix(temporary_delimiter + character):
            if current_token:
                tokens.append(current_token)
                current_token = ''
            if temporary_delimiter:
                tokens.append(temporary_delimiter)
                temporary_delimiter = ''
            current_token = character
        else:
            possible_delimiters = _check_prefix(temporary_delimiter + character)
            if len(possible_delimiters) == 0:
                if temporary_delimiter:
                    if current_token:
                        tokens.append(current_token)
                        current_token = ''
                    tokens.append(temporary_delimiter)
                    temporary_delimiter = character
                    if not _check_prefix(temporary_delimiter):
                        current_token = temporary_delimiter
                        temporary_delimiter = ''
                else:
                    current_token += character
            else:
                temporary_delimiter += character
        flag_escape = False
    if current_token:
        tokens.append(current_token)
    if temporary_delimiter:
        tokens.append(temporary_delimiter)
    return tokens
'''
Data Types
'''
_type_operations = {
    "_add": {
        -1: {-1: lambda self, v: _number(self[1] + v[1]),
             -2: lambda self, v: _string(str(self[1]) + v[1]),
             -3: lambda self, v: _number(self[1] + (1 if v[1] else 0))},
        -2: {-1: lambda self, v: _string(self[1] + str(v[1])),
             -2: lambda self, v: _string(self[1] + v[1]),
             -3: lambda self, v: _string(self[1] + ('true' if v[1] else 'false'))},
        -3: {-1: lambda self, v: _number((1 if self[1] else 0) + v[1]),
             -2: lambda self, v: _number(('true' if self[1] else 'false') + v[1]),
             -3: lambda self, v: _bool(self[1] or v[1])}
    },
    "_sub": {
        -1: {-1: lambda self, v: _number(self[1] - v[1]),
             -3: lambda self, v: _number(self[1] - (1 if v[1] else 0))},
        -2: {},
        -3: {-1: lambda self, v: _number((1 if self[1] else 0) - v[1]),
             -3: lambda self, v: _bool(self[1] and not v[1])}
    },
    "_mult": {
        -1: {-1: lambda self, v: _number(self[1] * v[1]),
             -2: lambda self, v: _string(v[1] * self[1]),
             -3: lambda self, v: _number(self[1] if v[1] else 0)},
        -2: {-1: lambda self, v: _string(self[1] * v[1]),
             -3: lambda self, v: _string(self[1] if v[1] else 0)},
        -3: {-1: lambda self, v: _number(v[1] if self[1] else 0),
             -2: lambda self, v: _string(v[1] if self[1] else 0),
             -3: lambda self, v: _bool(self[1] and v[1])}
    },
    "_divn": {
        -1: {-1: lambda self, v: _number(self[1] / v[1]),
             -3: lambda self, v: _number(self[1]) if v[1] else 1/0},
        -2: {-3: lambda self, v: _string(self[1]) if v[1] else 1/0},
        -3: {-1: lambda self, v: _number((1 / v[1]) if self[1] else 0)}
    },
    "_divf": {
        -1: {-1: lambda self, v: _number(int(self[1] / v[1])),
             -3: lambda self, v: _number(int(self[1])) if v[1] else 1/0},
        -2: {-3: lambda self, v: _string(self[1]) if v[1] else 1/0},
        -3: {-1: lambda self, v: _number(int(1 / v[1]) if self[1] else 0)}
    },
    "_mod": {
        -1: {-1: lambda self, v: _number(self[1] % v[1]),
             -2: lambda self, v: _string(v[1] % self[1]),
             -3: lambda self, v: _number(self[1]) if v[1] else 1/0},
        -2: {-1: lambda self, v: _string(self[1] % v[1]),
             -2: lambda self, v: _string(self[1] % v[1]),
             -3: lambda self, v: _string(self[1] % ('true' if v[1] else 'false'))},
        -3: {-1: lambda self, v: _number(1 % v[1] if self[1] else 0),
             -2: lambda self, v: _string(v[1] % ('true' if self[1] else 'false')),
             -3: lambda self, v: _bool(True) if v[1] else False / False}
    },
    "_less": {
        -1: {-1: lambda self, v: _bool(self[1] < v[1]),
             -3: lambda self, v: _bool(self[1] < (1 if v[1] else 0))},
        -2: {},
        -3: {-1: lambda self, v: _bool((1 if self[1] else 0) < v[1]),
             -3: lambda self, v: _bool(not self[1] and v[1])}
    },
    "_leq": {
        -1: {-1: lambda self, v: _bool(self[1] <= v[1]),
             -3: lambda self, v: _bool(self[1] <= (1 if v[1] else 0))},
        -2: {},
        -3: {-1: lambda self, v: _bool((1 if self[1] else 0) <= v[1]),
             -3: lambda self, v: _bool(not self[1] or v[1])}
    },
    "_greater": {
        -1: {-1: lambda self, v: _bool(self[1] > v[1]),
             -3: lambda self, v: _bool(self[1] > (1 if v[1] else 0))},
        -2: {},
        -3: {-1: lambda self, v: _bool((1 if self[1] else 0) > v[1]),
             -3: lambda self, v: _bool(self[1] and not v[1])}
    },
    "_geq": {
        -1: {-1: lambda self, v: _bool(self[1] >= v[1]),
             -3: lambda self, v: _bool(self[1] >= (1 if v[1] else 0))},
        -2: {},
        -3: {-1: lambda self, v: _bool((1 if self[1] else 0) >= v[1]),
             -3: lambda self, v: _bool(self[1] or not v[1])}
    },
    #default return false
    "_equals": {
        -1: {-1: lambda self, v: _bool(self[1] == v[1]),
             -3: lambda self, v: _bool((self[1] != 0) == v[1])},
        -2: {-2: lambda self, v: _bool(self[1] == v[1])},
        -3: {-1: lambda self, v: _bool(self[1] == (v[1] != 0))}
    },
    #default return true
    "_neq": {
        -1: {-1: lambda self, v: _bool(self[1] != v[1]),
             -3: lambda self, v: _bool((self[1] != 0) != v[1])},
        -2: {-2: lambda self, v: _bool(self[1] != v[1])},
        -3: {-1: lambda self, v: _bool(self[1] != (v[1] != 0))}
    },
    "_str": {
        -1: lambda self: str(self[1]),
        -2: lambda self: self[1],
        -3: lambda self: 'true' if self[1] else 'false'
    }
}
def _number(value = 0):
    return (-1, value)
def _string(value = ''):
    return (-2, value)
def _bool(value = False):
    return (-3, value)
_type_lookup = {-1: "number", -2: "string", -3: "bool"}
'''
Compiler
'''
_operator_lookup = {':=':'03','+':'04','-':'05','*':'06','/':'07','//':'08','**':'09','%':'0a','<':'13','<=':'14','>':'15','>=':'16','=':'17','!=':'18','+:':'19','-:':'1a','*:':'1b','/:':'1c','//:':'1d','**:':'1e','%:':'1f'}
_tokens = []
_token_index = 0
_consts = [_number(0), _number(1)]
_const_lookup = {0:0, 1:1}
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
    if token in _ending:
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
        if _peek() not in _ending:
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
        while _peek() not in _ending:
            _eval(if_scope)
            _next()
        end_if = len(scope["code"])
        scope["code"].append(None)
        scope["goto"][jump_else] = len(scope["code"])
        if _peek(2) == 'else':
            _next(2)
            if _peek() == 'if':
                _eval(scope)
            else:
                _next()
                while _peek() != '}':
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
        while _peek() not in _ending:
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
        while _peek() not in _ending:
            _eval(until_scope)
            _next()
        scope["code"].append('12{:02x}'.format(len(scope["goto"])))
        scope["goto"].append(repeat_until)
        scope["goto"][jump_until] = len(scope["code"])
    #manage other keywords here
    else:
        operators = []
        while _peek() not in _ending:
            token = _next()
            if _is_number(token) is not None:
                token_value = _number(_is_number(token))
                _add_const(token_value)
                scope["code"].append('00{:02x}'.format(_const_lookup[token_value]))
            elif _is_string(token):
                token = token[1:-1]
                token_value = _string(token)
                _add_const(token_value)
                scope["code"].append('00{:02x}'.format(_const_lookup[token_value]))
            elif _is_bool(token):
                token_value = _bool(token == 'true')
                _add_const(token_value)
                scope["code"].append('00{:02x}'.format(_const_lookup[token_value]))
            elif _is_variable(token):
                scope_defined = _peek() == '{'
                if scope_defined:
                    _next()
                    _eval(scope)
                    _next()
                scope_defined = '01' if scope_defined else '00'
                if _peek() in _opening:
                    _next()
                    num_args = 0
                    while _peek() not in _ending:
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
                elif _peek() in _self_operators:
                    operator = _next()
                    _eval(scope)
                    scope["code"].append(_operator_lookup[operator] + _get_var(token) + scope_defined)
                else:
                    scope["code"].append('01' + _get_var(token) + scope_defined)
            elif token in _opening:
                _eval(scope)
                _next()
            else:
                while operators and _operators[token] >= _operators[operators[-1]]:
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

def _compile():
    bytecode = []
    scope = _create_scope()
    while _peek() is not None:
        _eval(scope)
        _next()
    _condense(scope)
    return scope
'''
Bytecode executer
'''
def _exec(scope):
    bytecode = scope["code"]
    evaluation_stack = []
    byte_index = 0
    while byte_index < len(bytecode):
        command_termination = int(_get_byte(bytecode, byte_index), 16) * 2
        command = _get_byte(bytecode, byte_index+2)
        arguments = []
        byte_index += 4
        while byte_index < command_termination:
            arguments.append(int(_get_byte(bytecode, byte_index), 16))
            byte_index += 2
        if command == '00':
            evaluation_stack.append(_consts[arguments[0]])
        elif command == '01':
            temp_scope = scope
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()[1]):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            while temp_scope["parent"] and arguments[0] not in temp_scope["values"]:
                temp_scope = temp_scope["parent"]
            if arguments[0] not in temp_scope["values"]:
                raise NameError
            evaluation_stack.append(temp_scope["values"][arguments[0]])
        elif command == '02':
            temp_scope = scope
            new_value = evaluation_stack.pop()
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()[1]):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            temp_scope["values"][arguments[0]] = new_value
            evaluation_stack.append(new_value)
        elif command == '03':
            temp_scope = scope
            new_value = evaluation_stack.pop()
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()[1]):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            while temp_scope["parent"] and arguments[0] not in temp_scope["values"]:
                temp_scope = temp_scope["parent"]
            if arguments[0] not in temp_scope["values"]:
                raise NameError
            temp_scope["values"][arguments[0]] = new_value
            evaluation_stack.append(new_value)
        elif command == '04':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(_type_operations["_add"][a[0]][b[0]](a, b))
        elif command == '05':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(_type_operations["_sub"][a[0]][b[0]](a, b))
        elif command == '06':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(_type_operations["_mult"][a[0]][b[0]](a, b))
        elif command == '07':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(_type_operations["_divn"][a[0]][b[0]](a, b))
        elif command == '08':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(_type_operations["_divf"][a[0]][b[0]](a, b))
        elif command == '09':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(_type_operations["_pow"][a[0]][b[0]](a, b))
        elif command == '0a':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(_type_operations["_mod"][a[0]][b[0]](a, b))
        elif command == '0b':
            temp_scope = scope
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()[1]):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            temp_scope["values"][arguments[0]] = None
        elif command == '0c':
            num_args = arguments[1]
            arg_values = [evaluation_stack.pop() for arg_count in range(arguments[1])]
            temp_scope = scope
            if arguments[2]:
                for scope_count in range(evaluation_stack.pop()[1]):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            while temp_scope["parent"] and arguments[0] not in temp_scope["func"]:
                temp_scope = temp_scope["parent"]
            function = copy_scope(temp_scope["func"][arguments[0]])
            arg_count = -1
            for arg in function["values"]:
                function["values"][arg] = arg_values[arg_count]
                arg_count -= 1
            evaluation_stack.append(_exec(function))
        elif command == '0d':
            print_arguments = []
            for argument_count in range(arguments[0]):
                print_arguments.append(evaluation_stack.pop())
            for argument in range(arguments[0]-1, 0, -1):
                print(_type_operations["_str"][print_arguments[argument][0]](print_arguments[argument]), end = ' ')
            if print_arguments:
                print(_type_operations["_str"][print_arguments[0][0]](print_arguments[0]), end = '')
        elif command == '0e':
            print_arguments = []
            for argument_count in range(arguments[0]):
                print_arguments.append(evaluation_stack.pop())
            for argument in range(arguments[0]-1, 0, -1):
                print(_type_operations["_str"][print_arguments[argument][0]](print_arguments[argument]), end = ' ')
            if print_arguments:
                print(_type_operations["_str"][print_arguments[0][0]](print_arguments[0]), end = '')
            print()
        elif command == '0f':
            return evaluation_stack.pop()
        elif command == '10':
            if not evaluation_stack.pop()[1]:
                byte_index = scope["goto"][arguments[0]] * 2
        elif command == '11':
            if evaluation_stack.pop()[1]:
                byte_index = scope["goto"][arguments[0]] * 2
        elif command == '12':
            byte_index = scope["goto"][arguments[0]] * 2
            scope = scope["parent"]
        elif command == '13':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(_type_operations["_less"][a[0]][b[0]](a, b))
        elif command == '14':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(_type_operations["_leq"][a[0]][b[0]](a, b))
        elif command == '15':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(_type_operations["_greater"][a[0]][b[0]](a, b))
        elif command == '16':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(_type_operations["_geq"][a[0]][b[0]](a, b))
        elif command == '17':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            if a[0] in _type_operations["_equals"] and b[0] in _type_operations["_equals"][a[0]]:
                evaluation_stack.append(_type_operations["_equals"][a[0]][b[0]](a, b))
            else:
                evaluation_stack.append(_bool(False))
        elif command == '18':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            if a[0] in _type_operations["_neq"] and b[0] in _type_operations["_neq"][a[0]]:
                evaluation_stack.append(_type_operations["_neq"][a[0]][b[0]](a, b))
            else:
                evaluation_stack.append(_bool(True))
        elif command == '19':
            temp_scope = scope
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()[1]):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            while temp_scope["parent"] and arguments[0] not in temp_scope["values"]:
                temp_scope = temp_scope["parent"]
            if arguments[0] not in temp_scope["values"]:
                raise NameError
            b = evaluation_stack.pop()
            a = temp_scope["values"][arguments[0]]
            temp_scope["values"][arguments[0]] = _type_operations["_add"][a[0]][b[0]](a, b)
            evaluation_stack.append(temp_scope["values"][arguments[0]])
        elif command == '1a':
            temp_scope = scope
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()[1]):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            while temp_scope["parent"] and arguments[0] not in temp_scope["values"]:
                temp_scope = temp_scope["parent"]
            if arguments[0] not in temp_scope["values"]:
                raise NameError
            b = evaluation_stack.pop()
            a = temp_scope["values"][arguments[0]]
            temp_scope["values"][arguments[0]] = _type_operations["_sub"][a[0]][b[0]](a, b)
            evaluation_stack.append(temp_scope["values"][arguments[0]])
        elif command == '1b':
            temp_scope = scope
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()[1]):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            while temp_scope["parent"] and arguments[0] not in temp_scope["values"]:
                temp_scope = temp_scope["parent"]
            if arguments[0] not in temp_scope["values"]:
                raise NameError
            b = evaluation_stack.pop()
            a = temp_scope["values"][arguments[0]]
            temp_scope["values"][arguments[0]] = _type_operations["_mult"][a[0]][b[0]](a, b)
            evaluation_stack.append(temp_scope["values"][arguments[0]])
        elif command == '1c':
            temp_scope = scope
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()[1]):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            while temp_scope["parent"] and arguments[0] not in temp_scope["values"]:
                temp_scope = temp_scope["parent"]
            if arguments[0] not in temp_scope["values"]:
                raise NameError
            b = evaluation_stack.pop()
            a = temp_scope["values"][arguments[0]]
            temp_scope["values"][arguments[0]] = _type_operations["_divn"][a[0]][b[0]](a, b)
            evaluation_stack.append(temp_scope["values"][arguments[0]])
        elif command == '1d':
            temp_scope = scope
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()[1]):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            while temp_scope["parent"] and arguments[0] not in temp_scope["values"]:
                temp_scope = temp_scope["parent"]
            if arguments[0] not in temp_scope["values"]:
                raise NameError
            b = evaluation_stack.pop()
            a = temp_scope["values"][arguments[0]]
            temp_scope["values"][arguments[0]] = _type_operations["_divf"][a[0]][b[0]](a, b)
            evaluation_stack.append(temp_scope["values"][arguments[0]])
        elif command == '1e':
            temp_scope = scope
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()[1]):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            while temp_scope["parent"] and arguments[0] not in temp_scope["values"]:
                temp_scope = temp_scope["parent"]
            if arguments[0] not in temp_scope["values"]:
                raise NameError
            b = evaluation_stack.pop()
            a = temp_scope["values"][arguments[0]]
            temp_scope["values"][arguments[0]] = _type_operations["_pow"][a[0]][b[0]](a, b)
            evaluation_stack.append(temp_scope["values"][arguments[0]])
        elif command == '1f':
            temp_scope = scope
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()[1]):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            while temp_scope["parent"] and arguments[0] not in temp_scope["values"]:
                temp_scope = temp_scope["parent"]
            if arguments[0] not in temp_scope["values"]:
                raise NameError
            b = evaluation_stack.pop()
            a = temp_scope["values"][arguments[0]]
            temp_scope["values"][arguments[0]] = _type_operations["_mod"][a[0]][b[0]](a, b)
            evaluation_stack.append(temp_scope["values"][arguments[0]])
        elif command == '20':
            scope = scope["scopes"][arguments[0]]
        elif command == '21':
            scope = scope["parent"]
        elif command == '22':
            temp_scope = scope
            if arguments[2]:
                for scope_count in range(evaluation_stack.pop()[1]):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            temp_scope["func"][arguments[0]] = _func_data[arguments[1]]
'''
Bytecode Formatter
'''
_commands = {
    '00': 'push_const' ,
    '01': 'push_name'  ,
    '02': 'def_name'   ,
    '03': 'set_name'   ,
    '04': 'add'        ,
    '05': 'sub'        ,
    '06': 'mult'       ,
    '07': 'div_norm'   ,
    '08': 'div_floor'  ,
    '09': 'pow'        ,
    '0a': 'mod'        ,
    '0b': 'make_name'  ,
    '0c': 'call_func'  ,
    '0d': 'print'      ,
    '0e': 'println'    ,
    '0f': 'return'     ,
    '10': 'goto_false' ,
    '11': 'goto_true'  ,
    '12': 'goto'       ,
    '13': 'less'       ,
    '14': 'less_eq'    ,
    '15': 'greater'    ,
    '16': 'greater_eq' ,
    '17': 'equals'     ,
    '18': 'not_eq'     ,
    '19': 'add_name'   ,
    '1a': 'sub_name'   ,
    '1b': 'mult_name'  ,
    '1c': 'divn_name'  ,
    '1d': 'divf_name'  ,
    '1e': 'pow_name'   ,
    '1f': 'mod_name'   ,
    '20': 'goto_scope' ,
    '21': 'goto_parent',
    '22': 'def_func'   ,
}
def _get_byte(bytecode, byte_index):
    return bytecode[byte_index:byte_index+2]
def _format(scope):
    byte_index = 0
    instruction = 0
    while byte_index < len(scope["code"]):
        command_termination = _get_byte(scope["code"], byte_index)
        print(str(instruction).rjust(3), end = '\t' + ('    >>\t' if byte_index // 2 in scope["goto"] else '\t'))
        print(command_termination, end = '\t')
        byte_index += 2
        print(_commands[_get_byte(scope["code"], byte_index)].ljust(15), end = '')
        command_termination = int(command_termination, 16) * 2
        byte_index += 2
        while byte_index < command_termination:
            print(_get_byte(scope["code"], byte_index), end = '\t')
            byte_index += 2
        print()
        instruction += 1
'''
Main
'''
def main():
    global _tokens
    _tokens = _get_tokens()
    scope = _compile()
    if '-r' in _active_flags:
        print(_raw_input)
    if '-b' in _active_flags:
        print('GLOBAL')
        _format(scope)
        print()
    if '-f' in _active_flags:
        for count, function in enumerate(_func_data):
            print('FUNCTION {}'.format(count))
            _format(function)
        print()
    if '-g' in _active_flags:
        print('GLOBAL GOTOS')
        print(*['{:02x}'.format(i) for i in scope["goto"]])
        print()
    _exec(scope)
if __name__ == '__main__':
    main()
