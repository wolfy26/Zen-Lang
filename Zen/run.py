'''
'''
import lexer, compiler, interpreter, decompiler
from collections import deque
def run(debug = False, dash_num = 58):
    tokens = lexer.get_tokens(debug)
    scope = compiler.parse(tokens)
    if debug:
        debug_divider = '-' * dash_num
        print(debug_divider)
        print('GLOBAL')
        decompiler.parse(scope["code"])
        print(debug_divider)
        funcs = deque([(i, f) for i, f in enumerate(compiler._func_data)])
        for i, f in enumerate(compiler._func_data):
            print('FUNCTION', i)
            decompiler.parse(f["code"])
            print(debug_divider)
    interpreter.execute(scope, compiler._consts)
if __name__ == '__main__':
    run()
