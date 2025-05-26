"""
🎯 Enhanced Evaluator for RCX-π
Now with working beta-reduction!
"""

from .motif import Motif

class Evaluator:
    """Evaluates motifs with proper beta-reduction"""
    
    def __init__(self, rule_engine=None):
        self.rule_engine = rule_engine

    def evaluate_with_steps(self, motif):
        """Main evaluation method expected by REPL"""
        return {
            'result': motif,  # Just return the input unchanged for now
            'steps': [],
            'success': True
        }

    
    def evaluate(self, motif):
        """Evaluate a motif with step-by-step reduction"""
        steps = []
        current = motif
        
        while True:
            reduced = self.reduce_once(current)
            if reduced == current:  # No more reductions possible
                break
            
            steps.append({
                'rule': self.get_reduction_rule(current, reduced),
                'from': current,
                'to': reduced
            })
            current = reduced
        
        return current    

    def reduce_once(self, motif):
        """Perform one step of reduction"""
        if not isinstance(motif, Motif):
            return motif
        
        # Beta reduction for lambda application
        if motif.name == 'app' and len(motif.args) >= 2:
            func = motif.args[0]
            arg = motif.args[1]
            
            # If function is a lambda, perform beta reduction
            if isinstance(func, Motif) and func.name == 'lambda':
                return self.beta_reduce(func, arg)
            
            # Try reducing the function first
            reduced_func = self.reduce_once(func)
            if reduced_func != func:
                return Motif('app', [reduced_func, arg])
            
            # Try reducing the argument
            reduced_arg = self.reduce_once(arg)
            if reduced_arg != arg:
                return Motif('app', [func, reduced_arg])
        
        # Arithmetic reduction
        elif motif.name == 'add' and len(motif.args) >= 2:
            left = motif.args[0]
            right = motif.args[1]
            
            # If right is zero: add(x, zero) = x
            if isinstance(right, Motif) and right.name == 'zero':
                return left
            
            # If right is succ(y): add(x, succ(y)) = succ(add(x, y))
            if isinstance(right, Motif) and right.name == 'succ':
                return Motif('succ', [Motif('add', [left, right.args[0]])])
        
        # Recursively reduce arguments
        if hasattr(motif, 'args') and motif.args:
            new_args = []
            changed = False
            for arg in motif.args:
                reduced_arg = self.reduce_once(arg)
                new_args.append(reduced_arg)
                if reduced_arg != arg:
                    changed = True
            
            if changed:
                return Motif(motif.name, new_args)
        
        return motif
    
    def beta_reduce(self, lambda_expr, argument):
        """Perform beta reduction: (λx.body) arg = body[x := arg]"""
        if not isinstance(lambda_expr, Motif) or lambda_expr.name != 'lambda':
            return lambda_expr
        
        if len(lambda_expr.args) < 2:
            return lambda_expr
        
        variable = lambda_expr.args[0]  # The bound variable
        body = lambda_expr.args[1]      # The lambda body
        
        # Substitute argument for variable in body
        return self.substitute(body, variable, argument)
    
    def substitute(self, expr, var, replacement):
        """Substitute all occurrences of var with replacement in expr"""
        if not isinstance(expr, Motif):
            return expr
        
        # If this is the variable we're substituting, replace it
        if expr.name == 'var' and len(expr.args) > 0 and expr.args[0] == var:
            return replacement
        
        # If this is a lambda binding the same variable, don't substitute inside
        if expr.name == 'lambda' and len(expr.args) > 0 and expr.args[0] == var:
            return expr
        
        # Recursively substitute in arguments
        if hasattr(expr, 'args') and expr.args:
            new_args = [self.substitute(arg, var, replacement) for arg in expr.args]
            return Motif(expr.name, new_args)
        
        return expr
    
    def get_reduction_rule(self, before, after):
        """Identify which reduction rule was applied"""
        if isinstance(before, Motif):
            if before.name == 'app':
                return 'β-reduction'
            elif before.name == 'add':
                return 'addition'
            elif before.name == 'mult':
                return 'multiplication'
        return 'reduction'
