# rcx_pi/core/parser.py
"""
🎯 Enhanced Parser for RCX-π with Lambda Calculus Support
Handles both arithmetic and lambda expressions
"""

import re
from .motif import Motif

class Parser:
    """Enhanced parser supporting arithmetic and lambda calculus"""
    
    def __init__(self, arithmetic_domain=None, lambda_domain=None):
        self.arithmetic_domain = arithmetic_domain
        self.lambda_domain = lambda_domain
        
        # Precompiled patterns
        self.function_pattern = re.compile(r'(\w+)\s*$ (.*?) $ ')
        self.lambda_pattern = re.compile(r'[λ\\](\w+)\.(.+)')
    
    def parse_expression(self, text):
        """Parse any expression - lambda, arithmetic, or motif"""
        text = text.strip()
        
        # Try lambda expressions first
        lambda_result = self.parse_lambda(text)
        if lambda_result:
            return lambda_result
        
        # Try arithmetic expressions
        arithmetic_result = self.parse_arithmetic(text)
        if arithmetic_result:
            return arithmetic_result
        
        # Try app() function for lambda applications
        app_result = self.parse_application(text)
        if app_result:
            return app_result
        
        # Fall back to variable lookup
        return self.parse_variable(text)
    
    def parse_lambda(self, text):
        """Parse lambda expressions"""
        if not self.lambda_domain:
            return None
            
        text = text.strip()
        
        # Lambda abstractions: λx.x or \x.x
        if text.startswith('λ') or text.startswith('\\'):
            return self.lambda_domain.parse_lambda_expr(text)
        
        # Named lambda constants
        lambda_constants = {
            'LTRUE': 'LAMBDA_TRUE',
            'LFALSE': 'LAMBDA_FALSE', 
            'I': 'I',
            'K': 'K',
            'S': 'S',
            'Y': 'Y',
            'CZERO': 'CHURCH_ZERO',
            'CONE': 'CHURCH_ONE',
            'CTWO': 'CHURCH_TWO',
            'CTHREE': 'CHURCH_THREE'
        }
        
        if text in lambda_constants:
            return self.lambda_domain.variables[lambda_constants[text]]
        
        return None
    
    def parse_arithmetic(self, text):
        """Parse arithmetic expressions"""
        if not self.arithmetic_domain:
            return None
        
        # Function calls: add(X, Y), mult(X, Y), etc.
        match = self.function_pattern.match(text)
        if match:
            func_name = match.group(1)
            args_text = match.group(2)
            
            if func_name in ['add', 'mult', 'succ']:
                args = [self.parse_expression(arg.strip()) 
                       for arg in self.split_args(args_text)]
                return Motif(func_name, *args)
        
        # Named arithmetic constants
        arithmetic_constants = ['ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX']
        if text in arithmetic_constants:
            return self.arithmetic_domain.variables[text]
        
        return None
    
    def parse_application(self, text):
        """Parse function application: app(F, X)"""
        if not self.lambda_domain:
            return None
            
        match = self.function_pattern.match(text)
        if match and match.group(1) == 'app':
            args_text = match.group(2)
            args = [self.parse_expression(arg.strip()) 
                   for arg in self.split_args(args_text)]
            if len(args) == 2:
                return self.lambda_domain.app(args[0], args[1])
        
        return None
    
    def parse_variable(self, text):
        """Parse simple variables"""
        # Check both domains for variables
        if self.arithmetic_domain and text in self.arithmetic_domain.variables:
            return self.arithmetic_domain.variables[text]
        
        if self.lambda_domain and text in self.lambda_domain.variables:
            return self.lambda_domain.variables[text]
        
        # Create new variable
        return Motif('var', text)
    
    def split_args(self, args_text):
        """Split function arguments, respecting nested parentheses"""
        if not args_text.strip():
            return []
        
        args = []
        current_arg = ""
        paren_depth = 0
        
        for char in args_text:
            if char == ',' and paren_depth == 0:
                args.append(current_arg.strip())
                current_arg = ""
            else:
                if char == '(':
                    paren_depth += 1
                elif char == ')':
                    paren_depth -= 1
                current_arg += char
        
        if current_arg.strip():
            args.append(current_arg.strip())
        
        return args
