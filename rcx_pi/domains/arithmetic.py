# rcx_pi/domains/arithmetic.py
"""
🎯 Arithmetic Domain for RCX-π  
Implements Peano arithmetic with motif rewriting
"""

from ..core.motif import Motif

class ArithmeticDomain:
    """Arithmetic operations using Peano axioms"""
    
    def __init__(self):
        self.variables = {}
        self.setup_peano_numbers()
    
    def setup_peano_numbers(self):
        """Initialize basic Peano numbers"""
        self.variables = {
            'ZERO': Motif('zero'),
            'ONE': Motif('succ', Motif('zero')),
            'TWO': Motif('succ', Motif('succ', Motif('zero'))),
            'THREE': Motif('succ', Motif('succ', Motif('succ', Motif('zero')))),
            'FOUR': Motif('succ', Motif('succ', Motif('succ', Motif('succ', Motif('zero'))))),
            'FIVE': Motif('succ', Motif('succ', Motif('succ', Motif('succ', Motif('succ', Motif('zero')))))),
            'SIX': Motif('succ', Motif('succ', Motif('succ', Motif('succ', Motif('succ', Motif('succ', Motif('zero'))))))),
        }
    
    def add(self, x, y):
        """Create addition motif: add(x, y)"""
        return Motif('add', x, y)
    
    def mult(self, x, y):
        """Create multiplication motif: mult(x, y)"""
        return Motif('mult', x, y)
    
    def succ(self, x):
        """Create successor motif: succ(x)"""
        return Motif('succ', x)
    
    def zero(self):
        """Create zero motif"""
        return Motif('zero')
    
    def to_number(self, motif):
        """Convert Peano number to integer"""
        if not isinstance(motif, Motif):
            return None
        
        if motif.name == 'zero':
            return 0
        elif motif.name == 'succ' and len(motif.args) > 0:
            inner_value = self.to_number(motif.args[0])
            return inner_value + 1 if inner_value is not None else None
        
        return None
    
    def from_number(self, n):
        """Convert integer to Peano number"""
        if n < 0:
            return None
        
        result = Motif('zero')
        for _ in range(n):
            result = Motif('succ', result)
        
        return result
