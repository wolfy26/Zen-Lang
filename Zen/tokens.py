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
    return token[0] == token[-1] and (token[0] == '"' or token[0] == "'")

def bool(token):
    return token == 'true' or token == 'false'
