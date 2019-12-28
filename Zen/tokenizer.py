import grammar
import tokens

def _read_file(filename):
    try:
        if not filename.endswith('.zl'):
            filename += '.zl'
        with open(filename, "r") as file:
            while True:
                nextChar = file.read(1)
                if len(nextChar) == 1:
                    yield nextChar
                else:
                    return
    except FileNotFoundError:
        # handle FileNotFound exception
        print("File unable to be accessed.")

def _match_prefix(prefix, searches):
    return [search for search in searches if search.startswith(prefix)]

def _find_delims(delim_prefix):
    return sum((_match_prefix(delim_prefix, group) for group in grammar.DELIMS), [])

def tokenize(filename):
    current_token = ''
    temp_delim = ''
    string_flag = 0
    escape_flag = False
    for char in _read_file(filename):
        if not escape_flag and char == '\\':
            escape_flag = True
            continue
        if string_flag == 1:
            current_token += char
            if char == '"' and not escape_flag:
                string_flag = 0
                escape_flag = False
                yield current_token
                current_token = ''
        elif string_flag == 2:
            current_token += char
            if char == "'" and not escape_flag:
                string_flag = 0
                escape_flag = False
                yield current_token
                current_token = ''
        elif char.isspace():
            if current_token:
                yield current_token
                current_token = ''
        elif char == '"' and not escape_flag:
            if current_token:
                yield current_token
            if temp_delim:
                yield temp_delim
                temp_delim = ''
            current_token = char
            string_flag = 1
        elif char == "'" and not escape_flag:
            if current_token:
                yield current_token
            if temp_delim:
                yield temp_delim
                temp_delim = ''
            current_token = char
            string_flag = 2
        elif char == '.' and tokens.number(current_token + char) is not None:
            current_token += char
        elif char == '-' and not _find_delims(temp_delim + char):
            if current_token:
                yield current_token
            if temp_delim:
                yield temp_delim
                temp_delim = ''
            current_token = char
        elif not _find_delims(temp_delim + char):
            if temp_delim:
                if current_token:
                    yield current_token
                    current_token = ''
                yield temp_delim
                if not _find_delims(char):
                    current_token = char
                    temp_delim = ''
                else:
                    temp_delim = char
            else:
                current_token += char
        else:
            temp_delim += char
        escape_flag = False
    if current_token:
        yield current_token
    if temp_delim:
        yield temp_delim
