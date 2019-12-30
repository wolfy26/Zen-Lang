_type_operations = {
    "_add": {
        -1: {-1: lambda self, v: _number(self[1] + v[1]),
             -2: lambda self, v: _string(str(self[1]) + v[1]),
             -3: lambda self, v: _number(self[1] + (1 if v[1] else 0))},
        -2: {-1: lambda self, v: _string(self[1] + str(v[1])),
             -2: lambda self, v: _string(self[1] + v[1]),
             -3: lambda self, v: _string(self[1] + ('true' if v[1] else 'false'))},
        -3: {-1: lambda self, v: _number((1 if self[1] else 0) + v[1]),
             -2: lambda self, v: _number(('true' if self[1] else 'false') + v[1]),
             -3: lambda self, v: _bool(self[1] or v[1])}
    },
    "_sub": {
        -1: {-1: lambda self, v: _number(self[1] - v[1]),
             -3: lambda self, v: _number(self[1] - (1 if v[1] else 0))},
        -2: {},
        -3: {-1: lambda self, v: _number((1 if self[1] else 0) - v[1]),
             -3: lambda self, v: _bool(self[1] and not v[1])}
    },
    "_mult": {
        -1: {-1: lambda self, v: _number(self[1] * v[1]),
             -2: lambda self, v: _string(v[1] * self[1]),
             -3: lambda self, v: _number(self[1] if v[1] else 0)},
        -2: {-1: lambda self, v: _string(self[1] * v[1]),
             -3: lambda self, v: _string(self[1] if v[1] else 0)},
        -3: {-1: lambda self, v: _number(v[1] if self[1] else 0),
             -2: lambda self, v: _string(v[1] if self[1] else 0),
             -3: lambda self, v: _bool(self[1] and v[1])}
    },
    "_divn": {
        -1: {-1: lambda self, v: _number(self[1] / v[1]),
             -3: lambda self, v: _number(self[1]) if v[1] else 1/0},
        -2: {-3: lambda self, v: _string(self[1]) if v[1] else 1/0},
        -3: {-1: lambda self, v: _number((1 / v[1]) if self[1] else 0)}
    },
    "_divf": {
        -1: {-1: lambda self, v: _number(int(self[1] / v[1])),
             -3: lambda self, v: _number(int(self[1])) if v[1] else 1/0},
        -2: {-3: lambda self, v: _string(self[1]) if v[1] else 1/0},
        -3: {-1: lambda self, v: _number(int(1 / v[1]) if self[1] else 0)}
    },
    "_mod": {
        -1: {-1: lambda self, v: _number(self[1] % v[1]),
             -2: lambda self, v: _string(v[1] % self[1]),
             -3: lambda self, v: _number(self[1]) if v[1] else 1/0},
        -2: {-1: lambda self, v: _string(self[1] % v[1]),
             -2: lambda self, v: _string(self[1] % v[1]),
             -3: lambda self, v: _string(self[1] % ('true' if v[1] else 'false'))},
        -3: {-1: lambda self, v: _number(1 % v[1] if self[1] else 0),
             -2: lambda self, v: _string(v[1] % ('true' if self[1] else 'false')),
             -3: lambda self, v: _bool(True) if v[1] else False / False}
    },
    "_less": {
        -1: {-1: lambda self, v: _bool(self[1] < v[1]),
             -3: lambda self, v: _bool(self[1] < (1 if v[1] else 0))},
        -2: {},
        -3: {-1: lambda self, v: _bool((1 if self[1] else 0) < v[1]),
             -3: lambda self, v: _bool(not self[1] and v[1])}
    },
    "_leq": {
        -1: {-1: lambda self, v: _bool(self[1] <= v[1]),
             -3: lambda self, v: _bool(self[1] <= (1 if v[1] else 0))},
        -2: {},
        -3: {-1: lambda self, v: _bool((1 if self[1] else 0) <= v[1]),
             -3: lambda self, v: _bool(not self[1] or v[1])}
    },
    "_greater": {
        -1: {-1: lambda self, v: _bool(self[1] > v[1]),
             -3: lambda self, v: _bool(self[1] > (1 if v[1] else 0))},
        -2: {},
        -3: {-1: lambda self, v: _bool((1 if self[1] else 0) > v[1]),
             -3: lambda self, v: _bool(self[1] and not v[1])}
    },
    "_geq": {
        -1: {-1: lambda self, v: _bool(self[1] >= v[1]),
             -3: lambda self, v: _bool(self[1] >= (1 if v[1] else 0))},
        -2: {},
        -3: {-1: lambda self, v: _bool((1 if self[1] else 0) >= v[1]),
             -3: lambda self, v: _bool(self[1] or not v[1])}
    },
    #default return false
    "_equals": {
        -1: {-1: lambda self, v: _bool(self[1] == v[1]),
             -3: lambda self, v: _bool((self[1] != 0) == v[1])},
        -2: {-2: lambda self, v: _bool(self[1] == v[1])},
        -3: {-1: lambda self, v: _bool(self[1] == (v[1] != 0))}
    },
    #default return true
    "_neq": {
        -1: {-1: lambda self, v: _bool(self[1] != v[1]),
             -3: lambda self, v: _bool((self[1] != 0) != v[1])},
        -2: {-2: lambda self, v: _bool(self[1] != v[1])},
        -3: {-1: lambda self, v: _bool(self[1] != (v[1] != 0))}
    },
    "_str": {
        -1: lambda self: str(self[1]),
        -2: lambda self: self[1],
        -3: lambda self: 'true' if self[1] else 'false'
    }
}
