'''
'''
from decompiler import get_byte
from compiler import copy_scope
_consts = []
def _eval(bytecode, scope):
    evaluation_stack = []
    byte_index = 0
    while byte_index < len(bytecode):
        command_termination = int(get_byte(bytecode, byte_index), 16) * 2
        command = get_byte(bytecode, byte_index+2)
        arguments = []
        byte_index += 4
        while byte_index < command_termination:
            arguments.append(int(get_byte(bytecode, byte_index), 16))
            byte_index += 2
        if command == '00':
            evaluation_stack.append(_consts[arguments[0]])
        elif command == '01':
            temp_scope = scope
            for scope_count in range(arguments[0]):
                temp_scope = temp_scope["parent_scope"]
            evaluation_stack.append(temp_scope["values"][arguments[1]])
        elif command == '02':
            temp_scope = scope
            for scope_count in range(arguments[0]):
                temp_scope = temp_scope["parent_scope"]
            temp_scope["values"][arguments[1]] = evaluation_stack[-1]
        elif command == '03':
            temp_scope = scope
            for scope_count in range(arguments[0]):
                temp_scope = temp_scope["parent_scope"]
            if arguments[0] not in temp_scope["values"]:
                raise NameError
            temp_scope["values"][arguments[1]] = evaluation_stack[-1]
        elif command == '04':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(a + b)
        elif command == '05':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop() if evaluation_stack else 0
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
            temp_scope = scope
            for scope_count in range(arguments[0]):
                temp_scope = temp_scope["parent_scope"]
            temp_scope["values"][arguments[1]] = None
        elif command == '0c':
            temp_scope = scope
            for scope_count in range(arguments[0]):
                temp_scope = temp_scope["parent_scope"]
            function = temp_scope["func_data"][temp_scope["funcs"][arguments[1]]]
            function_scope = copy_scope(function[1])
            num_args = arguments[2]
            for argument_count in range(num_args-1, -1, -1):
                function_scope["values"][argument_count] = evaluation_stack.pop()
            evaluation_stack.append(_eval(function[0], function_scope))
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
        elif command == '10':
            if not evaluation_stack.pop():
                byte_index = scope["goto"][arguments[0]] * 2
        elif command == '11':
            if evaluation_stack.pop():
                byte_index = scope["goto"][arguments[0]] * 2
        elif command == '12':
            byte_index = scope["goto"][arguments[0]] * 2
        elif command == '13':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(a < b)
        elif command == '14':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(a <= b)
        elif command == '15':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(a > b)
        elif command == '16':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(a >= b)
        elif command == '17':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(a == b)
        elif command == '18':
            b = evaluation_stack.pop()
            a = evaluation_stack.pop()
            evaluation_stack.append(a != b)
        elif command == '19':
            temp_scope = scope
            for scope_count in range(arguments[0]):
                temp_scope = temp_scope["parent_scope"]
            temp_scope["values"][arguments[1]] += evaluation_stack.pop()
            evaluation_stack.append(temp_scope["values"][arguments[1]])
        elif command == '1a':
            temp_scope = scope
            for scope_count in range(arguments[0]):
                temp_scope = temp_scope["parent_scope"]
            temp_scope["values"][arguments[1]] -= evaluation_stack.pop()
            evaluation_stack.append(temp_scope["values"][arguments[1]])
        elif command == '1b':
            temp_scope = scope
            for scope_count in range(arguments[0]):
                temp_scope = temp_scope["parent_scope"]
            temp_scope["values"][arguments[1]] *= evaluation_stack.pop()
            evaluation_stack.append(temp_scope["values"][arguments[1]])
        elif command == '1c':
            temp_scope = scope
            for scope_count in range(arguments[0]):
                temp_scope = temp_scope["parent_scope"]
            temp_scope["values"][arguments[1]] /= evaluation_stack.pop()
            evaluation_stack.append(temp_scope["values"][arguments[1]])
        elif command == '1d':
            temp_scope = scope
            for scope_count in range(arguments[0]):
                temp_scope = temp_scope["parent_scope"]
            temp_scope["values"][arguments[1]] = int(temp_scope["values"][arguments[0]]/evaluation_stack.pop())
            evaluation_stack.append(temp_scope["values"][arguments[1]])
        elif command == '1e':
            temp_scope = scope
            for scope_count in range(arguments[0]):
                temp_scope = temp_scope["parent_scope"]
            temp_scope["values"][arguments[1]] **= evaluation_stack.pop()
            evaluation_stack.append(temp_scope["values"][arguments[1]])
        elif command == '1f':
            temp_scope = scope
            for scope_count in range(arguments[0]):
                temp_scope = temp_scope["parent_scope"]
            temp_scope["values"][arguments[1]] %= evaluation_stack.pop()
            evaluation_stack.append(temp_scope["values"][arguments[1]])
def execute(bytecode, scope, consts):
    global _consts
    _consts = consts
    _eval(bytecode, scope)
