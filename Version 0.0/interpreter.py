'''
[interpreter.py] runs a series of machine instructions
'''
import compiler, decompiler
def _eval(bytecode = '', names = [], values = {}, consts = [], funcs = [], func_content = {}):
    evaluation_stack = []
    byte_index = 0
    while byte_index < len(bytecode):
        command_termination = int(decompiler.get_byte(bytecode, byte_index)) * 2
        command = decompiler.get_byte(bytecode, byte_index+2)
        arguments = []
        byte_index += 4
        while byte_index <= command_termination:
            arguments.append(int(decompiler.get_byte(bytecode, byte_index)))
            byte_index += 2
        if command == '00':
            evaluation_stack.append(consts[arguments[0]])
        elif command == '01':
            evaluation_stack.append(values[names[arguments[0]]])
        elif command == '02':
            values[names[arguments[0]]] = evaluation_stack.pop()
        elif command == '03':
            values[names[arguments[0]]] = evaluation_stack.pop()
        elif command == '04':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(a + b)
        elif command == '05':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(a - b)
        elif command == '06':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(a * b)
        elif command == '07':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(a / b)
        elif command == '08':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(int(a / b))
        elif command == '09':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(a ** b)
        elif command == '0a':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(a % b)
        elif command == '0b':
            values[arguments[0]] = None
        elif command == '0c':
            call_function = func_content[funcs[arguments[0]]]
            function_values = {}
            num_args = arguments[1]
            for argument_count in range(num_args-1, -1, -1):
                function_values[call_function[1][argument_count]] = evaluation_stack.pop()
            evaluation_stack.append(_eval(call_function[0], call_function[1], function_values, call_function[2]))
        elif command == '0d':
            print_arguments = []
            for argument_count in range(arguments[0]):
                print_arguments.append(evaluation_stack.pop())
            for argument in range(arguments[0]-1, 0, -1):
                print(print_arguments[argument], end = ' ')
            if print_arguments:
                print(print_arguments[0], end = '')
        elif command == '0e':
            print_arguments = []
            for argument_count in range(arguments[0]):
                print_arguments.append(evaluation_stack.pop())
            for argument in range(arguments[0]-1, 0, -1):
                print(print_arguments[argument], end = ' ')
            if print_arguments:
                print(print_arguments[0], end = '')
            print()
        elif command == '0f':
            return evaluation_stack.pop()
def execute():
    _eval(compiler._bytecode, compiler._names, {}, compiler._consts, compiler._funcs, compiler._func_content)
