# rcx_pi/core/rules.py
"""
🎯 Enhanced Rules Engine with Lambda Calculus Support
Handles both arithmetic rewriting and lambda reduction
"""

from .motif import Motif

class RuleEngine:
    """Rule engine supporting arithmetic and lambda calculus"""
    
    def __init__(self, arithmetic_domain=None, lambda_domain=None):
        self.arithmetic_domain = arithmetic_domain
        self.lambda_domain = lambda_domain
        self.rules = []
        self.setup_rules()
    
    def setup_rules(self):
        """Initialize all reduction rules"""
        # Arithmetic rules
        if self.arithmetic_domain:
            self.rules.extend([
                ("add_zero", self._add_zero),
                ("add_succ", self._add_succ),
                ("mult_zero", self._mult_zero),
                ("mult_succ", self._mult_succ),
            ])
        
        # Lambda calculus rules
        if self.lambda_domain:
            self.rules.extend(self.lambda_domain.rules)
    
    def apply_rules(self, motif):
        """Apply the first matching rule"""
        # Try lambda rules first (they're more fundamental)
        if self.lambda_domain:
            for rule_name, rule_func in self.lambda_domain.rules:
                result = rule_func(motif)
                if result and not self._motifs_equal(result, motif):
                    return result, f"λ-{rule_name}"
        
        # Then try arithmetic rules
        if self.arithmetic_domain:
            # Arithmetic rules
            result, rule_name = self._try_arithmetic_rules(motif)
            if result:
                return result, rule_name
        
        return None, None
    
    def _try_arithmetic_rules(self, motif):
        """Try all arithmetic rules"""
        # Addition rules
        if motif.name == "add":
            # add(zero, X) → X
            if (len(motif.args) >= 2 and 
                motif.args[0].name == "zero"):
                return motif.args[1], "μ(add, μ(zero), $X) → $X"
            
            # add(succ(X), Y) → succ(add(X, Y))
            elif (len(motif.args) >= 2 and 
                  motif.args[0].name == "succ"):
                inner = motif.args[0].args[0]
                return Motif("succ", Motif("add", inner, motif.args[1])), \
                       "μ(add, μ(succ, $X), $Y) → μ(succ, μ(add, $X, $Y))"
        
        # Multiplication rules
        elif motif.name == "mult":
            # mult(zero, Y) → zero
            if (len(motif.args) >= 2 and 
                motif.args[0].name == "zero"):
                return Motif("zero"), "μ(mult, μ(zero), $Y) → μ(zero)"
            
            # mult(succ(X), Y) → add(Y, mult(X, Y))
            elif (len(motif.args) >= 2 and 
                  motif.args[0].name == "succ"):
                inner = motif.args[0].args[0]
                return Motif("add", motif.args[1], Motif("mult", inner, motif.args[1])), \
                       "μ(mult, μ(succ, $X), $Y) → μ(add, $Y, μ(mult, $X, $Y))"
        
        return None, None
    
    def _add_zero(self, motif):
        """Rule: add(zero, X) → X"""
        if (motif.name == "add" and len(motif.args) >= 2 and motif.args[0].name == "zero"):
            return motif.args[1]
        return None
    
    def _add_succ(self, motif):
        """Rule: add(succ(X), Y) → succ(add(X, Y))"""
        if (motif.name == "add" and len(motif.args) >= 2 and motif.args[0].name == "succ"):
            inner = motif.args[0].args[0]
            return Motif("succ", Motif("add", inner, motif.args[1]))
        return None
    
    def _mult_zero(self, motif):
        """Rule: mult(zero, Y) → zero"""
        if (motif.name == "mult" and len(motif.args) >= 2 and motif.args[0].name == "zero"):
            return Motif("zero")
        return None
    
    def _mult_succ(self, motif):
        """Rule: mult(succ(X), Y) → add(Y, mult(X, Y))"""
        if (motif.name == "mult" and len(motif.args) >= 2 and motif.args[0].name == "succ"):
            inner = motif.args[0].args[0]
            return Motif("add", motif.args[1], Motif("mult", inner, motif.args[1]))
        return None
    
    def _motifs_equal(self, m1, m2):
        """Check if two motifs are equal"""
        if not isinstance(m1, Motif) or not isinstance(m2, Motif):
            return m1 == m2
        
        if m1.name != m2.name or len(m1.args) != len(m2.args):
            return False
        
        return all(self._motifs_equal(a1, a2) for a1, a2 in zip(m1.args, m2.args))
    
    def reduce_completely(self, motif, max_steps=100):
        """Reduce motif until normal form"""
        steps = []
        current = motif
        
        for step_num in range(1, max_steps + 1):
            result, rule = self.apply_rules(current)
            if not result:
                break  # Normal form reached
            
            steps.append({
                'step': step_num,
                'rule': rule,
                'from': current,
                'to': result
            })
            current = result
        
        return current, steps
