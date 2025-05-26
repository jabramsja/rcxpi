"""Core RCX-π data structures."""

class Motif:
    def __init__(self, name, *args):
        self.name = name
        self.args = tuple(args)
    
    def __eq__(self, other):
        return (isinstance(other, Motif) and 
                self.name == other.name and 
                self.args == other.args)
    
    def __hash__(self):
        return hash((self.name, self.args))
    
    def __repr__(self):
        if self.args:
            args_str = ", ".join(str(arg) for arg in self.args)
            return f"μ({self.name}, {args_str})"
        return f"μ({self.name})"

def μ(name, *args):
    """Convenience function for creating motifs."""
    return Motif(name, *args)

class Variable:
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return f"${self.name}"
    
    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name
    
    def __hash__(self):
        return hash(("VAR", self.name))
