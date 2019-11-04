'''
'''
import lexer, compiler, interpreter, decompiler
from collections import deque
def run(debug = False, dash_num = 58):
    tokens = lexer.get_tokens(debug)
    bytecode, scope, consts = compiler.parse(tokens)
    if debug:
        debug_divider = '-' * dash_num
        print(debug_divider)
        print('GLOBAL')
        decompiler.parse(bytecode)
        print(debug_divider)
        funcs = deque([(i, "GLOBAL", scope["func_data"][i]) for i in scope["func_data"]])
        while funcs:
            func = funcs.popleft()
            func_name = '{0} in {1}'.format(func[0], func[1])
            print(func_name)
            decompiler.parse(func[2][0])
            print(debug_divider)
            funcs.extend([(i, func_name, func[2][1]["func_data"][i]) for i in func[2][1]["func_data"]])
    interpreter.execute(bytecode, scope, consts)
if __name__ == '__main__':
    run()
