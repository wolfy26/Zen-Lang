ENV_FLAGS  = ('r', 'b', 'f', 'g')

OPCODES    = ('PUSH_CONST', # 00
              'PUSH_NAME' , # 01
              'DEF_NAME'  , # 02
              'SET_NAME'  , # 03
              'MAKE_NAME' , # 04
              'ADD'       , # 05
              'SUB'       , # 06
              'MULT'      , # 07
              'DIV_N'     , # 08
              'DIV_F'     , # 09
              'POW'       , # 0a
              'MOD'       , # 0b
              'CALL_FUNC' , # 0c
              'PRINT'     , # 0d
              'PRINTLN'   , # 0e
              'RETURN'    , # 0f
              'JUMP_F'    , # 10
              'JUMP_T'    , # 11
              'GOTO'      , # 12
              'LESS'      , # 13
              'LESS_EQ'   , # 14
              'GREATER'   , # 15
              'GREATER_EQ', # 16
              'EQUALS'    , # 17
              'NOT_EQ'    , # 18
              'S_ADD'     , # 19
              'S_SUB'     , # 1a
              'S_MULT'    , # 1b
              'S_DIVN'    , # 1c
              'S_DIVF'    , # 1d
              'S_POW'     , # 1e
              'S_MOD'     , # 1f
              'GO_SCOPE'  , # 20
              'GO_PARENT' , # 21
              'PUSH_FUNC' , # 22
              'BIT_NOT'   , # 23
              'BIT_AND'   , # 24
              'BIT_XOR'   , # 25
              'BIT_OR'    , # 26
              'LOG_NOT'   , # 27
              'LOG_AND'   , # 28
              'LOG_XOR'   , # 29
              'LOG_OR'    , # 2a
              'S_BAND'    , # 2b
              'S_BXOR'    , # 2c
              'S_BOR'     , # 2d
              'S_INC'     , # 2e
              'S_DEC'     ) # 2f

OPEN_DELIM = ('(', '{', '[')
END_DELIM  = (')', '}', ']', ';', ',')
MISC_DELIM = ('.')

BINARY_OPS = ('%', '^', '&', '|', '*', '/', '-', '+', '<', '>', '^^', '&&', '||', '!=', '=', '<=', '>=', '**', '//')
UNARY_OPS  = ('!', '~', '++', '--')
ASSIGN_OPS = (':=', '%:', '^:', '&:', '*:', '/:', '-:', '+:', '|:', '**:', '//:')

DELIMS = (OPEN_DELIM, END_DELIM, MISC_DELIM, BINARY_OPS, UNARY_OPS, ASSIGN_OPS)

OP_ORDER   = (('++', '--'),
              ('!', '~'),
              ('**'),
              ('*', '/', '//', '%'),
              ('+', '-'),
              ('<', '>', '<=', '>='),
              ('=', '!='),
              ('&'),
              ('^'),
              ('|'),
              ('&&'),
              ('^^'),
              ('||'),
              ASSIGN_OPS)

OP_LOOKUP  = {':=' : 0x03,
              '+'  : 0x05,
              '-'  : 0x06,
              '*'  : 0x07,
              '/'  : 0x08,
              '//' : 0x09,
              '**' : 0x0a,
              '%'  : 0x0b,
              '<'  : 0x13,
              '<=' : 0x14,
              '>'  : 0x15,
              '>=' : 0x16,
              '='  : 0x17,
              '!=' : 0x18,
              '+:' : 0x19,
              '-:' : 0x1a,
              '*:' : 0x1b,
              '/:' : 0x1c,
              '//:': 0x1d,
              '**:': 0x1e,
              '%:' : 0x1f,
              '~'  : 0x23,
              '&'  : 0x24,
              '^'  : 0x25,
              '|'  : 0x26,
              '!'  : 0x27,
              '&&' : 0x28,
              '^^' : 0x29,
              '||' : 0x2a,
              '&:' : 0x2b,
              '^:' : 0x2c,
              '|:' : 0x2d,
              '++' : 0x2e,
              '--' : 0x2f}
