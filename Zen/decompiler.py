'''
'''
_commands = {
    '00': 'push_const',
    '01': 'push_name' ,
    '02': 'def_name'  ,
    '03': 'set_name'  ,
    '04': 'add'       ,
    '05': 'sub'       ,
    '06': 'mult'      ,
    '07': 'div_norm'  ,
    '08': 'div_floor' ,
    '09': 'pow'       ,
    '0a': 'mod'       ,
    '0b': 'make_name' ,
    '0c': 'call_func' ,
    '0d': 'print'     ,
    '0e': 'println'   ,
    '0f': 'return'    ,
    '10': 'if_false'  ,
    '11': 'if_true'   ,
    '12': 'goto'      ,
    '13': 'less'      ,
    '14': 'less_eq'   ,
    '15': 'greater'   ,
    '16': 'greater_eq',
    '17': 'equals'    ,
    '18': 'not_eq'    ,
    '19': 'add_name'  ,
    '1a': 'sub_name'  ,
    '1b': 'mult_name' ,
    '1c': 'divn_name' ,
    '1d': 'divf_name' ,
    '1e': 'pow_name'  ,
    '1f': 'mod_name'
}
def get_byte(bytecode, byte_index):
    return bytecode[byte_index:byte_index+2]
def parse(bytecode):
    byte_index = 0
    instruction = 0
    while byte_index < len(bytecode):
        command_termination = get_byte(bytecode, byte_index)
        print(str(instruction).rjust(3), end = '\t\t')
        print(command_termination, end = '\t')
        byte_index += 2
        print(_commands[get_byte(bytecode, byte_index)].ljust(15), end = '')
        command_termination = int(command_termination, 16) * 2
        byte_index += 2
        while byte_index < command_termination:
            print(get_byte(bytecode, byte_index), end = '\t')
            byte_index += 2
        print()
        instruction += 1
