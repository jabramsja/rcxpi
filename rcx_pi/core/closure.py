"""Closure operations for RCX-π."""

from .motif import Motif

class Closure:
    """Represents a closure in RCX-π."""
    
    def __init__(self, motif):
        self.motif = motif
    
    def __repr__(self):
        return f"Closure({self.motif})"
    
    def evaluate(self):
        """Evaluate the closure."""
        return self.motif
