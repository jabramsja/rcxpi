"""Projection rules for RCX-π."""

from .motif import Motif, Variable

class Projection:
    """A projection rule that transforms one motif pattern to another."""
    
    def __init__(self, pattern, target):
        self.pattern = pattern
        self.target = target
    
    def __repr__(self):
        return f"Projection({self.pattern} → {self.target})"
    
    def apply(self, motif):
        """Apply this projection to a motif."""
        from .patterns import apply_projection
        return apply_projection(motif, self)
