'''
[parser.py] converts a list of tokens to bytecode

Bytecode:
    00 -> push_const   [const_index]           -> add constant to stack
    01 -> push_name    [name_index]            -> add value of variable to stack
    02 -> def_name     [name_index]            -> define variable with value on stack
    03 -> set_name     [name_index]            -> set variable to value on stack
    04 -> add                                  -> add two values on stack
    05 -> sub                                  -> (second-to-top value on stack) minus (top value on stack)
    06 -> mult                                 -> multiply two values on stack
    07 -> div_norm                             -> (second-to-top value on stack) divided by (top value on stack)
    08 -> div_floor                            -> (second-to-top value on stack) integer divide (top value on stack)
    09 -> pow                                  -> raise second-to-top value on stack to top value on stack
    0a -> mod                                  -> (second-to-top value on stack) mod (top value on stack)
    0b -> make_name    [name_index]            -> create variable with no value
    0c -> call_func    [func_index] [num_args] -> call function, pop arguments off stack
    0d -> print        [num_args]              -> special print function, pop arguments off stack
    0e -> println      [num_args]              -> same as print, except prints with new line
    0f -> return                               -> return top value on stack
'''
import lexer
_operator_lookup = {'+':'04', '-':'05', '*':'06', '/':'07', '//':'08', '**':'09', '%':'0a'}
_tokens = []
_names = []
_consts = []
_funcs = []
_name_lookup = {}
_const_lookup = {}
_func_lookup = {}
_func_content = {}
_token_index = 0
_bytecode = ''
def _get_offset(bytecode, instruction):
    return '%02d' % ((len(bytecode) + len(instruction)) // 2 + 1)
def _add_instruction(bytecode, instruction):
    return _get_offset(bytecode, instruction) + instruction
def _eval(bytecode, names, name_lookup, consts, const_lookup):
    global _token_index
    current_token = _tokens[_token_index]
    print(_tokens[0:_token_index+1])
    _token_index += 1
    if current_token in lexer.ending_delimiters: #end of expression
        return bytecode
    elif current_token == 'def': #variable creation
        var_name = _tokens[_token_index]
        if _tokens[_token_index + 1] == '=': #variable assignment: def [var_name] = [value];
            _token_index += 2
            bytecode = _eval(bytecode, names, name_lookup, consts, const_lookup)
            if var_name not in name_lookup:
                name_lookup[var_name] = len(names)
                names.append(var_name)
            bytecode += _add_instruction(bytecode, '02%02d' % name_lookup[var_name])
            bytecode += _add_instruction(bytecode, '01%02d' % name_lookup[var_name])
        elif _tokens[_token_index+1] == '(': #function creation: def [var_name] () {}
            _token_index += 2
            if var_name not in _func_content:
                _func_lookup[var_name] = len(_funcs)
                _funcs.append(var_name)
            func_names = []
            func_name_lookup = {}
            func_consts = []
            func_const_lookup = {}
            arg_name = _tokens[_token_index]
            if arg_name not in lexer.ending_delimiters:
                while True:
                    func_name_lookup[arg_name] = len(func_names)
                    func_names.append(arg_name)
                    _token_index += 1
                    if _tokens[_token_index] == ')':
                        break
                    else:
                        _token_index += 1
                        arg_name = _tokens[_token_index]
            _token_index += 1
            func_bytecode = ''
            while _tokens[_token_index-1] != '}':
                func_bytecode = _eval(func_bytecode, func_names, func_name_lookup, func_consts, func_const_lookup)
            _func_content[var_name] = (func_bytecode, func_names, func_consts)
        else: #variable creation: def [var_name];
            if var_name not in name_lookup:
                name_lookup[var_name] = len(names)
                names.append(var_name)
            bytecode += _add_instruction(bytecode, '0b%02d' % name_lookup[var_name])
    elif current_token == 'return':
        if _tokens[_token_index] in lexer.ending_delimiters:
            if None not in const_lookup:
                const_lookup[None] = len(consts)
                consts.append(None)
            bytecode += _add_instruction(bytecode, '00%02d' % const_lookup[None])
        else:
            bytecode = _eval(bytecode, names, name_lookup, consts, const_lookup)
        bytecode += _add_instruction(bytecode, '0f')
    #add more keywords here
    else: #evaluate expression
        operators = []
        while current_token not in lexer.ending_delimiters:
            if lexer.is_number(current_token):
                const_value = float(current_token)
                if const_value not in const_lookup:
                    const_lookup[const_value] = len(consts)
                    consts.append(const_value)
                bytecode += _add_instruction(bytecode, '00%02d' % const_lookup[const_value])
            elif lexer.is_string(current_token):
                const_value = current_token[1:-1]
                if const_value not in const_lookup:
                    const_lookup[const_value] = len(consts)
                    consts.append(const_value)
                bytecode += _add_instruction(bytecode, '00%02d' % const_lookup[const_value])
            elif lexer.is_variable(current_token):
                if _tokens[_token_index] == '(':
                    func_name = current_token
                    print("function:", func_name)
                    _token_index += 1
                    num_arguments = 0
                    current_token = _tokens[_token_index]
                    print('token of {}:'.format(func_name),current_token,_token_index)
                    if current_token not in lexer.ending_delimiters:
                        while True:
                            bytecode = _eval(bytecode, names, name_lookup, consts, const_lookup)
                            num_arguments += 1
                            current_token = _tokens[_token_index]
                            if _tokens[_token_index-1] in lexer.ending_delimiters:
                                break
                    print('done with function', func_name, 'at token', _token_index)
                    if func_name == 'print': #special print functions
                        bytecode += _add_instruction(bytecode, '0d%02d' % num_arguments)
                    elif func_name == 'println':
                        bytecode += _add_instruction(bytecode, '0e%02d' % num_arguments)
                    else:
                        bytecode += _add_instruction(bytecode, '0c%02d%02d' % (_func_lookup[func_name], num_arguments))
                    _token_index += 1
                else:
                    bytecode += _add_instruction(bytecode, '01%02d' % name_lookup[current_token])
            elif current_token in lexer.opening_delimiters:
                bytecode = _eval(bytecode, names, name_lookup, consts, const_lookup)
            elif current_token in lexer.binary_delimiters:
                while operators and lexer.binary_delimiters[current_token] >= lexer.binary_delimiters[operators[-1]]:
                    bytecode += _add_instruction(bytecode, _operator_lookup[operators.pop()])
                operators.append(current_token)
            current_token = _tokens[_token_index]
            _token_index += 1
        while operators:
            bytecode += _add_instruction(bytecode, _operator_lookup[operators.pop()])
    print('eval ended at', _token_index)
    return bytecode

def parse(tokens):
    global _tokens, _bytecode
    _tokens = tokens
    while _token_index < len(_tokens):
        _bytecode = _eval(_bytecode, _names, _name_lookup, _consts, _const_lookup)
    return _bytecode
