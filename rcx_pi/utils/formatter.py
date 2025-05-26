# rcx_pi/utils/formatter.py
"""
🎯 Formatter for RCX-π Expressions
Handles pretty-printing of motifs and lambda expressions
"""

from ..core.motif import Motif

class Formatter:
    """Formats motifs and expressions for display"""
    
    def __init__(self):
        pass
    
    def format_motif(self, motif):
        """Format a motif for display"""
        if not isinstance(motif, Motif):
            return str(motif)
        
        # Handle different motif types
        if motif.name == 'zero':
            return "ZERO"
        
        elif motif.name == 'succ':
            # Convert Peano numbers to readable form
            count = self._count_successors(motif)
            if count is not None:
                return f"SUCC^{count}(ZERO)" if count > 0 else "ZERO"
            return f"succ({self.format_motif(motif.args[0])})"
        
        elif motif.name == 'add' and len(motif.args) >= 2:
            return f"add({self.format_motif(motif.args[0])}, {self.format_motif(motif.args[1])})"
        
        elif motif.name == 'mult' and len(motif.args) >= 2:
            return f"mult({self.format_motif(motif.args[0])}, {self.format_motif(motif.args[1])})"
        
        elif motif.name == 'app' and len(motif.args) >= 2:
            return f"app({self.format_motif(motif.args[0])}, {self.format_motif(motif.args[1])})"
        
        elif motif.name == 'lambda' and len(motif.args) >= 2:
            var_name = motif.args[0]
            body = self.format_motif(motif.args[1])
            return f"λ{var_name}.{body}"
        
        elif motif.name == 'var' and len(motif.args) >= 1:
            return str(motif.args[0])
        
        # Default formatting
        if not motif.args:
            return motif.name
        
        args_str = ", ".join(self.format_motif(arg) for arg in motif.args)
        return f"{motif.name}({args_str})"
    
    def _count_successors(self, motif):
        """Count number of successors in a Peano number"""
        if not isinstance(motif, Motif):
            return None
        
        if motif.name == 'zero':
            return 0
        elif motif.name == 'succ' and len(motif.args) > 0:
            inner_count = self._count_successors(motif.args[0])
            return inner_count + 1 if inner_count is not None else None
        
        return None
    
    def format_step(self, step):
        """Format a reduction step for display"""
        rule = step.get('rule', 'unknown')
        from_expr = self.format_motif(step.get('from', ''))
        to_expr = self.format_motif(step.get('to', ''))
        
        return f"{rule}: {from_expr} → {to_expr}"
    
    def format_evaluation_result(self, original, result, steps):
        """Format complete evaluation result"""
        lines = []
        lines.append(f"Input: {self.format_motif(original)}")
        
        if steps:
            lines.append("Steps:")
            for i, step in enumerate(steps, 1):
                lines.append(f"  {i}. {self.format_step(step)}")
        
        lines.append(f"Result: {self.format_motif(result)}")
        
        return "\n".join(lines)
