'''
'''
from sys import argv
import re

delimiters = {'!', '%', '^', '&', '*', '(', ')', '-', '+', ':=', '{', '}', '[', ']', '|', ';', ':', '<', '>', ',', '.', '?', '/',
               '&&', '||', '!=', '^=', '&=', '*:', '-:', '+:', '=', '|=', '<=', '>=', '/:', '//:' '++', '--', '**', '//'}
ending_delimiters = {')', '}', ']', ';', ','}
opening_delimiters = {'(', '{', '['}
operator_delimiters = {'%':1,'^':4,'&':3,'*':1,'-':2,'+':2,'|':5,'<':6,'>':6,'/':1,'&&':7,'||':8,'!=':6,'=':6,'<=':6,'>=':6,'**':0,'//':1,
                       ':=':7,'+:':7,'-:':7,'*:':7,'/:':7,'//:':7,'**:':7,'%:':7}
self_operator = {':=', '+:', '-:', '*:', '/:', '//:', '**:', '%:'}
def _get_filename():
    if len(argv) > 1:
        return argv[1]
    else:
        raise FileNotFoundError('File not specified')

def _read_file():
    filename = _get_filename()
    #infer .zl extension
    if filename[-3:] != '.zl':
        filename += '.zl'
    with open(filename, 'r') as f:
        return f.read()

def _check_prefix(token):
    prefixes = []
    for delimiter in delimiters:
        if delimiter.startswith(token):
            prefixes.append(delimiter)
    return prefixes

def number(token):
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return None

def is_variable(token):
    return re.match('^[a-zA-Z_]\\w*$', token)

def is_string(token):
    return token[0] == token[-1] and (token[0] == "'" or token[0] == '"')

def _split_tokens(debug):
    raw_input = _read_file()
    if debug:
        print(raw_input)
    tokens = []
    current_token = ''
    temporary_delimiter = ''
    flag_string = 0
    flag_escape = False
    for character in raw_input:
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
        elif character.isspace(): # Whitespace is also a token delimiter, but don't treat it as a token
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
        elif character == '.' and number(current_token + character) is not None:
            current_token += character
        elif character == '-' and not current_token and not _check_prefix(temporary_delimiter + character):
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

def get_tokens(debug = False):
    return _split_tokens(debug)
