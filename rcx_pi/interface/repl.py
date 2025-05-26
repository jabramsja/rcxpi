"""RCX-π interactive REPL interface."""

from ..core.motif import μ
from ..core.evaluator import SimpleInteractiveEvaluator
from ..domains.arithmetic import ZERO, ONE, TWO, THREE, FOUR, FIVE, SIX, ARITHMETIC_RULES

class RCXPiREPL:
    """Interactive REPL for RCX-π expressions."""
    
    def __init__(self, rules=None):
        self.evaluator = SimpleInteractiveEvaluator(rules or ARITHMETIC_RULES)
        self.variables = {
            'ZERO': ZERO,
            'ONE': ONE,
            'TWO': TWO,
            'THREE': THREE,
            'FOUR': FOUR,
            'FIVE': FIVE, 
            'SIX': SIX
        }
    
    def run(self):
        """Main REPL loop."""
        print("🚀 RCX-π REPL - Type expressions to evaluate!")
        print("   Available: ZERO, ONE, TWO, THREE, FOUR, FIVE, SIX")
        print("   Functions: add(X, Y), succ(X), mult(X, Y)")
        print("   Commands: help, exit, vars")
        print()
        
        while True:
            try:
                expr = input("rcx-π> ").strip()
                
                if expr in ['exit', 'quit']:
                    print("   Goodbye!")
                    break
                elif expr == 'help':
                    self._show_help()
                elif expr == 'vars':
                    self._show_vars()
                elif expr.startswith('add(') and expr.endswith(')'):
                    self._handle_add(expr)
                elif expr.startswith('succ(') and expr.endswith(')'):
                    self._handle_succ(expr)
                elif expr.startswith('mult(') and expr.endswith(')'):
                    self._handle_mult(expr)
                elif expr in self.variables:
                    result = self.variables[expr]
                    print(f"   {expr} = {result}\n")
                else:
                    print("   Usage: add(X, Y), succ(X), or variable name")
                    print("   Type 'help' for more info\n")
                    
            except KeyboardInterrupt:
                print("\n   Goodbye!")
                break
            except Exception as e:
                print(f"   Error: {e}\n")
    
    def _show_help(self):
        print("   RCX-π Commands:")
        print("   • add(X, Y)  - Add two numbers")
        print("   • mult(X, Y) - Multiply two numbers")
        print("   • succ(X)    - Successor of X") 
        print("   • vars       - Show variables")
        print("   • exit       - Quit")
        print()
    
    def _show_vars(self):
        print("   Variables:")
        for name, value in self.variables.items():
            print(f"   • {name} = {value}")
        print()
    
    def _handle_add(self, expr):
        inner = expr[4:-1]
        parts = inner.split(',')
        if len(parts) == 2:
            x_name = parts[0].strip()
            y_name = parts[1].strip()
            if x_name in self.variables and y_name in self.variables:
                x_val = self.variables[x_name]
                y_val = self.variables[y_name]
                expr_motif = μ("add", x_val, y_val)
                print()
                result = self.evaluator.evaluate_interactive(expr_motif)
                print()
            else:
                print(f"   Unknown variables. Available: {list(self.variables.keys())}\n")
        else:
            print("   Usage: add(VAR1, VAR2)\n")
    
    def _handle_succ(self, expr):
        inner = expr[5:-1]
        if inner in self.variables:
            x_val = self.variables[inner]
            result = μ("succ", x_val)
            print(f"   succ({inner}) = {result}\n")
        else:
            print(f"   Unknown variable: {inner}\n")

    def _handle_mult(self, expr):
        inner = expr[5:-1] 
        parts = inner.split(',')
        if len(parts) == 2:
            x_name = parts[0].strip()
            y_name = parts[1].strip()
            if x_name in self.variables and y_name in self.variables:
                x_val = self.variables[x_name]
                y_val = self.variables[y_name]
                expr_motif = μ("mult", x_val, y_val)
                print()
                result = self.evaluator.evaluate_interactive(expr_motif)
                print()
            else:
                print(f"   Unknown variables. Available: {list(self.variables.keys())}\n")
        else:
            print("   Usage: mult(VAR1, VAR2)\n")
