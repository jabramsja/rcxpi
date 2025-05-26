"""
🎯 Lambda Calculus ENCODED in RCX-π
Shows how λ-calculus emerges from motif projections
"""

from ..core.motif import Motif, μ
from ..core.projection import Projection
from ..core.closure import Closure

class LambdaViaRCX:
    """Lambda calculus implemented purely through RCX-π motifs and projections"""
    
    def __init__(self):
        # Core lambda combinators as pure motifs
        self.I = μ("λ", μ("x"), μ("x"))  # Identity: λx.x
        self.K = μ("λ", μ("x"), μ("λ", μ("y"), μ("x")))  # Constant: λx.λy.x
        self.S = μ("λ", μ("x"), μ("λ", μ("y"), μ("λ", μ("z"), 
                    μ("app", μ("app", μ("x"), μ("z")), 
                           μ("app", μ("y"), μ("z"))))))
        
        # Boolean logic via motifs
        self.TRUE = self.K  # TRUE = K
        self.FALSE = μ("λ", μ("x"), μ("λ", μ("y"), μ("y")))  # FALSE = λx.λy.y
        
        # Church numerals as motifs
        self.ZERO = μ("λ", μ("f"), μ("λ", μ("x"), μ("x")))
        self.ONE = μ("λ", μ("f"), μ("λ", μ("x"), μ("app", μ("f"), μ("x"))))
        self.TWO = μ("λ", μ("f"), μ("λ", μ("x"), 
                     μ("app", μ("f"), μ("app", μ("f"), μ("x")))))
        
        # Projection rules for beta-reduction
        self.projections = [
            # β-reduction: (λx.M)N → M[x:=N]
            Projection(
                μ("app", μ("λ", μ("var", "x"), μ("var", "M")), μ("var", "N")),
                μ("substitute", μ("var", "M"), μ("var", "x"), μ("var", "N"))
            ),
            
            # I x → x
            Projection(
                μ("app", self.I, μ("var", "x")),
                μ("var", "x")
            ),
            
            # K x y → x  
            Projection(
                μ("app", μ("app", self.K, μ("var", "x")), μ("var", "y")),
                μ("var", "x")
            )
        ]
    
    def app(self, func, arg):
        """Application as a motif"""
        return μ("app", func, arg)
    
    def lambda_abs(self, var, body):
        """Lambda abstraction as a motif"""
        return μ("λ", μ("var", var), body)
    
    def apply_projections(self, motif, max_steps=10):
        """Apply projection rules to reduce a motif"""
        current = motif
        steps = []
        
        for step in range(max_steps):
            reduced = False
            for projection in self.projections:
                result = projection.apply(current)
                if result and result != current:
                    steps.append({
                        'step': step + 1,
                        'rule': f"projection: {projection.pattern} → {projection.target}",
                        'from': current,
                        'to': result
                    })
                    current = result
                    reduced = True
                    break
            
            if not reduced:
                break
        
        return current, steps
    
    def demonstrate_encoding(self):
        """Show how lambda calculus emerges from RCX-π motifs"""
        print("🎯 Lambda Calculus emerging from RCX-π motifs:")
        print(f"   I combinator: {self.I}")
        print(f"   K combinator: {self.K}")
        print(f"   Application: {self.app(self.I, μ('var', 'x'))}")
        
        # Show reduction
        expr = self.app(self.I, μ("const", "hello"))
        result, steps = self.apply_projections(expr)
        
        print(f"\n🔥 Reduction: {expr}")
        for step in steps:
            print(f"   Step {step['step']}: {step['from']} → {step['to']}")
        print(f"   Result: {result}")

def test_lambda_via_rcx():
    """Test the lambda calculus encoding"""
    print("🎯 Testing Lambda Calculus via RCX-π\n")
    
    lam = LambdaViaRCX()
    
    # Basic identity test
    print("🧪 Testing I combinator:")
    identity_app = lam.app(lam.I, μ("example"))
    result, steps = lam.apply_projections(identity_app)
    print(f"   Expression: {identity_app}")
    for step in steps:
        print(f"   {step['rule']}: {step['from']} → {step['to']}")
    print(f"   Result: {result}\n")
    
    # Show that we're using pure motifs
    print("🔬 Pure RCX-π motifs used:")
    print(f"   I = {lam.I}")
    print(f"   K = {lam.K}")
    print(f"   TRUE = {lam.TRUE}")
    print(f"   ZERO = {lam.ZERO}")

if __name__ == "__main__":
    test_lambda_via_rcx()
