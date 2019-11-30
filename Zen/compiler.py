import tokenizer
import tokens
import grammar
import collections

def _init(filename):
    global _get_tokens, _tokens
    _get_tokens = tokenizer.tokenize(filename)
    _tokens = collections.deque()

def _peek(n = 0):
    while n >= len(x):
        _tokens.append(next(_get_tokens))
    return _tokens[n]

def _next(n = 0):
    t = _peek(n)
    for i in range(n):
        _tokens.popleft()
    return t
