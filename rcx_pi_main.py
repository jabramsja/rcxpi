# rcx_pi_main.py
"""
🎯 RCX-π REPL with Lambda Calculus Support
Interactive evaluation of arithmetic and lambda expressions
"""

import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rcx_pi.domains.arithmetic import ArithmeticDomain
from rcx_pi.domains.lambda_calculus import LambdaCalculus
from rcx_pi.core.parser import Parser
from rcx_pi.core.rules import RuleEngine
from rcx_pi.core.evaluator import Evaluator
from rcx_pi.utils.formatter import Formatter

class RCXPiREPL:
    """Enhanced REPL with lambda calculus support"""
    
    def __init__(self):
        self.arithmetic_domain = ArithmeticDomain()
        self.lambda_domain = LambdaCalculus()
        self.parser = Parser(self.arithmetic_domain, self.lambda_domain)
        self.rule_engine = RuleEngine(self.arithmetic_domain, self.lambda_domain)
        self.evaluator = Evaluator(self.rule_engine)
        self.formatter = Formatter()
    
    def run(self):
        """Run the interactive REPL"""
        self.print_welcome()
        
        while True:
            try:
                user_input = input("rcx-π> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'exit':
                    print("   Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    self.print_help()
                elif user_input.lower() == 'vars':
                    self.print_variables()
                else:
                    self.evaluate_expression(user_input)
                    
            except KeyboardInterrupt:
                print("\n   Use 'exit' to quit")
            except Exception as e:
                print(f"   Error: {e}")
    
    def print_welcome(self):
        """Print welcome message"""
        print("=" * 60)
        print("🎯 RCX-π MODULAR SYSTEM WITH LAMBDA CALCULUS")
        print("=" * 60)
        print("🚀 RCX-π REPL - Type expressions to evaluate!")
        print("   Arithmetic: ZERO, ONE, TWO, add(X, Y), mult(X, Y)")
        print("   Lambda: I, K, S, Y, \\x.x, app(F, X)")
        print("   Church: CZERO, CONE, LTRUE, LFALSE")
        print("   Commands: help, exit, vars")
        print()
    
    def print_help(self):
        """Print help information"""
        print("   RCX-π Commands:")
        print("   • Arithmetic:")
        print("     - add(X, Y)    - Add two numbers")
        print("     - mult(X, Y)   - Multiply two numbers") 
        print("     - succ(X)      - Successor of X")
        print("   • Lambda Calculus:")
        print("     - app(F, X)    - Apply function F to X")
        print("     - \\x.x         - Lambda abstraction")
        print("     - I, K, S, Y   - Famous combinators")
        print("   • Variables:")
        print("     - vars         - Show all variables")
        print("     - help         - Show this help")
        print("     - exit         - Quit")
    
    def print_variables(self):
        """Print all available variables"""
        print("   Variables:")
        print("   • Arithmetic:")
        for name, expr in self.arithmetic_domain.variables.items():
            print(f"     - {name} = {self.formatter.format_motif(expr)}")
        
        print("   • Lambda Calculus:")
        for name, expr in self.lambda_domain.variables.items():
            lambda_str = self.lambda_domain.pretty_print_lambda(expr)
            print(f"     - {name} = {lambda_str}")
    
    def evaluate_expression(self, text):
        """Evaluate and display expression"""
        try:
            # Parse the expression
            motif = self.parser.parse_expression(text)
            if not motif:
                print(f"   Could not parse: {text}")
                return
            
            # Check if it's a simple lookup
            if self.is_simple_lookup(text, motif):
                if hasattr(motif, 'name') and motif.name == 'lambda':
                    result_str = self.lambda_domain.pretty_print_lambda(motif)
                    print(f"   {text} = {result_str}")
                else:
                    result_str = self.formatter.format_motif(motif)
                    print(f"   {text} = {result_str}")
                return
            
            # Full evaluation with steps
            response = self.evaluator.evaluate_with_steps(motif)
            result = response["result"]
            steps = response["steps"]

            
            if not steps:
                # No reduction needed
                if hasattr(result, 'name') and result.name == 'lambda':
                    result_str = self.lambda_domain.pretty_print_lambda(result)
                else:
                    result_str = self.formatter.format_motif(result)
                print(f"   {text} = {result_str}")
                return
            
            # Show detailed evaluation
            print(f"\n🌟 RCX-π INTERACTIVE EVALUATOR 🌟")
            
            start_str = self.format_expression_for_display(motif)
            print(f"\n📍 START: {start_str}")
            print("=" * 60)
            
            for i, step in enumerate(steps, 1):
                print(f"⚡ STEP {i}")
                print(f"   Rule: {step['rule']}")
                
                from_str = self.format_expression_for_display(step['from'])
                to_str = self.format_expression_for_display(step['to'])
                
                print(f"   From: {from_str}")
                print(f"   To:   {to_str}")
                print()
            
            final_str = self.format_expression_for_display(result)
            print(f"✅ COMPLETE: {final_str}")
            
        except Exception as e:
            print(f"   Error evaluating '{text}': {e}")
    
    def is_simple_lookup(self, text, motif):
        """Check if this is just a variable lookup"""
        # Check arithmetic variables
        if text in self.arithmetic_domain.variables:
            return True
        # Check lambda variables  
        if text in self.lambda_domain.variables:
            return True
        return False
    
    def format_expression_for_display(self, expr):
        """Format expression for display, handling both arithmetic and lambda"""
        if hasattr(expr, 'name') and expr.name in ['lambda', 'app', 'var']:
            return self.lambda_domain.pretty_print_lambda(expr)
        else:
            return self.formatter.format_motif(expr)

def main():
    """Main entry point"""
    repl = RCXPiREPL()
    repl.run()

if __name__ == "__main__":
    main()
