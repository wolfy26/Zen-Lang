import re

def number(token):
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return None

def string(token):
    return len(token) >= 2 and token[0] == token[-1] and (token[0] == '"' or token[0] == "'")

def bool(token):
    return token == 'true' or token == 'false'

def variable(token):
    return re.match('^[a-zA-Z_]\\w*$', token)
