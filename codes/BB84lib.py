# Quantum Key Distribution simulation: BB84 protocol
# by Manuel Maiuolo (manuelmaiuolo@gmail.com)
# BB84lib.py - version 1.0

from random import randint

class Basis:
    def __init__(self, value = None):
        self.value = None
        if type(value) is str:
            value = value.upper()
            if value in ['Z', 'X']:
                self.value = value
        if self.value is None:
            # default: computational basis
            self.value = 'Z'

    def __str__(self):
        return self.value

    def set_from_b(self, b):
        b = str(b)
        if b == '0':
            self.value = 'Z'
        elif b == '1':
            self.value = 'X'
        else:
            raise ValueError("bit in string b is neither 0 nor 1!")
            

class Qubit:
    def __init__(self, value = None):
        value = str(value)
        if value in ['0', '1', '+', '-']:
            self.value = value
        else:  # default: |0>
            self.value = '0'

    def __str__(self):
        # ket notation
        return '|' + self.value + '>'

    def set_from_a_and_basis(self, a, basis):
        a = str(a)
        if (a != '0') and (a != '1'):
            raise ValueError("bit in string a is neither 0 nor 1!")
        if not isinstance(basis, Basis):
            raise ValueError("basis is not an instance of the Basis class!")
        
        if basis.value == 'Z':
            self.value = a
        else:  # basis.value == 'X'
            if a == '0':
                self.value = '+'
            else:  # a == '1'
                self.value = '-'

    def measure(self, basis):
        if (basis.value == 'Z') == (self.value == '0' or self.value == '1'):
            # measurement is made in the same basis as the qubit polarization
            # -> qubit collapses on the same value: no change is needed
            return +1 if (self.value == '0' or self.value == '+') else -1
        else:
            # measurement is made in the other basis
            # -> qubit randomly collapses on a new value
            result = randint(0, 1) * 2 - 1  # will be +1 or -1
            if basis.value == 'Z':
                self.value = '0' if (result == +1) else '1'
            else:  # basis.value == 'X'
                self.value = '+' if (result == +1) else '-'
            return result

def quantum_list_to_compact_string(qlist):
    # where qlist is a list of Qubit instances or Basis instances
    info = ""  # will be the compact string representing qubits OR basis
    for qelement in qlist:
        info += str(qelement.value)
    return info



