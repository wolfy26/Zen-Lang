'''
'''
from decompiler import get_byte
from compiler import copy_scope
from compiler import _func_data
_consts = []
def _eval(scope):
    bytecode = scope["code"]
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
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            while temp_scope["parent"] and arguments[0] not in temp_scope["values"]:
                temp_scope = temp_scope["parent"]
            if arguments[0] not in temp_scope["values"]:
                raise NameError
            evaluation_stack.append(temp_scope["values"][arguments[0]])
        elif command == '02':
            temp_scope = scope
            new_value = evaluation_stack.pop()
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            temp_scope["values"][arguments[0]] = new_value
            evaluation_stack.append(new_value)
        elif command == '03':
            temp_scope = scope
            new_value = evaluation_stack.pop()
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            while temp_scope["parent"] and arguments[0] not in temp_scope["values"]:
                temp_scope = temp_scope["parent"]
            if arguments[0] not in temp_scope["values"]:
                raise NameError
            temp_scope["values"][arguments[0]] = new_value
            evaluation_stack.append(new_value)
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
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            temp_scope["values"][arguments[0]] = None
        elif command == '0c':
            num_args = arguments[1]
            arg_values = [evaluation_stack.pop() for arg_count in range(arguments[1])]
            temp_scope = scope
            if arguments[2]:
                for scope_count in range(evaluation_stack.pop()):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            while temp_scope["parent"] and arguments[0] not in temp_scope["func"]:
                temp_scope = temp_scope["parent"]
            function = copy_scope(temp_scope["func"][arguments[0]])
            arg_count = -1
            for arg in function["values"]:
                function["values"][arg] = arg_values[arg_count]
                arg_count -= 1
            evaluation_stack.append(_eval(function))
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
            scope = scope["parent"]
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
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            while temp_scope["parent"] and arguments[0] not in temp_scope["values"]:
                temp_scope = temp_scope["parent"]
            if arguments[0] not in temp_scope["values"]:
                raise NameError
            temp_scope["values"][arguments[0]] += evaluation_stack.pop()
            evaluation_stack.append(temp_scope["values"][arguments[0]])
        elif command == '1a':
            temp_scope = scope
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            while temp_scope["parent"] and arguments[0] not in temp_scope["values"]:
                temp_scope = temp_scope["parent"]
            if arguments[0] not in temp_scope["values"]:
                raise NameError
            temp_scope["values"][arguments[0]] -= evaluation_stack.pop()
            evaluation_stack.append(temp_scope["values"][arguments[0]])
        elif command == '1b':
            temp_scope = scope
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            while temp_scope["parent"] and arguments[0] not in temp_scope["values"]:
                temp_scope = temp_scope["parent"]
            if arguments[0] not in temp_scope["values"]:
                raise NameError
            temp_scope["values"][arguments[0]] *= evaluation_stack.pop()
            evaluation_stack.append(temp_scope["values"][arguments[0]])
        elif command == '1c':
            temp_scope = scope
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            while temp_scope["parent"] and arguments[0] not in temp_scope["values"]:
                temp_scope = temp_scope["parent"]
            if arguments[0] not in temp_scope["values"]:
                raise NameError
            temp_scope["values"][arguments[0]] /= evaluation_stack.pop()
            evaluation_stack.append(temp_scope["values"][arguments[0]])
        elif command == '1d':
            temp_scope = scope
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            while temp_scope["parent"] and arguments[0] not in temp_scope["values"]:
                temp_scope = temp_scope["parent"]
            if arguments[0] not in temp_scope["values"]:
                raise NameError
            temp_scope["values"][arguments[0]] //= evaluation_stack.pop()
            evaluation_stack.append(temp_scope["values"][arguments[0]])
        elif command == '1e':
            temp_scope = scope
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            while temp_scope["parent"] and arguments[0] not in temp_scope["values"]:
                temp_scope = temp_scope["parent"]
            if arguments[0] not in temp_scope["values"]:
                raise NameError
            temp_scope["values"][arguments[0]] **= evaluation_stack.pop()
            evaluation_stack.append(temp_scope["values"][arguments[0]])
        elif command == '1f':
            temp_scope = scope
            if arguments[1]:
                for scope_count in range(evaluation_stack.pop()):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            while temp_scope["parent"] and arguments[0] not in temp_scope["values"]:
                temp_scope = temp_scope["parent"]
            if arguments[0] not in temp_scope["values"]:
                raise NameError
            temp_scope["values"][arguments[0]] //= evaluation_stack.pop()
            evaluation_stack.append(temp_scope["values"][arguments[0]])
        elif command == '20':
            scope = scope["scopes"][arguments[0]]
        elif command == '21':
            scope = scope["parent"]
        elif command == '22':
            temp_scope = scope
            if arguments[2]:
                for scope_count in range(evaluation_stack.pop()):
                    if not temp_scope["parent"]:
                        break
                    temp_scope = temp_scope["parent"]
            temp_scope["func"][arguments[0]] = _func_data[arguments[1]]
def execute(scope, consts):
    global _consts
    _consts = consts
    _eval(scope)
