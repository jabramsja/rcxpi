"""Pattern matching engine for RCX-π."""

from .motif import Motif, Variable

def pattern_match(motif, pattern, bindings):
    """Match a motif against a pattern, updating bindings."""
    if isinstance(pattern, Variable):
        if pattern in bindings:
            return bindings[pattern] == motif
        bindings[pattern] = motif
        return True
    
    if not isinstance(motif, Motif) or not isinstance(pattern, Motif):
        return motif == pattern
    
    if motif.name != pattern.name or len(motif.args) != len(pattern.args):
        return False
    
    for m_arg, p_arg in zip(motif.args, pattern.args):
        if not pattern_match(m_arg, p_arg, bindings):
            return False
    
    return True

def substitute_variables(template, bindings):
    """Substitute variables in template with their bindings."""
    if isinstance(template, Variable):
        return bindings[template]
    
    if isinstance(template, Motif):
        from .motif import μ
        return μ(template.name, *[
            substitute_variables(arg, bindings) for arg in template.args
        ])
    
    return template

def apply_projection(motif, projection):
    """Apply a projection rule to a motif."""
    bindings = {}
    if pattern_match(motif, projection.pattern, bindings):
        return substitute_variables(projection.target, bindings)
    return None

def apply_projection_deep(motif, projection):
    """Apply projection to motif or any of its subterms."""
    # First try the whole motif
    bindings = {}
    if pattern_match(motif, projection.pattern, bindings):
        return substitute_variables(projection.target, bindings)
    
    # Then try each argument recursively
    if isinstance(motif, Motif):
        from .motif import μ
        new_args = []
        changed = False
        for arg in motif.args:
            new_arg = apply_projection_deep(arg, projection)
            if new_arg is not None:
                new_args.append(new_arg)
                changed = True
            else:
                new_args.append(arg)
        
        if changed:
            return μ(motif.name, *new_args)
    
    return None
