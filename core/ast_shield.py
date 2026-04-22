"""
AST Safety Shield v1.0.0
Static analysis layer for Nova Output Engine.
Scans code structure BEFORE execution to detect forbidden patterns.

Educational Note:
-----------------
AST (Abstract Syntax Tree) parsing lets us inspect code structure
without executing it. We walk the tree looking for dangerous nodes:
- Import of forbidden modules (os, subprocess, shutil, sys)
- Attribute access to dangerous methods (eval, exec, compile)
- Path traversal patterns in strings (../, /etc/, C:\\\\Windows)

This is a "blast door" that fires BEFORE the sandbox even runs.
"""

import ast
from typing import Tuple, List, Set
from dataclasses import dataclass


@dataclass
class ShieldResult:
    """Result of AST safety scan."""
    safe: bool
    violations: List[str]
    risk_score: float  # 0.0 = clean, 1.0 = critical danger


# Forbidden imports - these modules enable system access
FORBIDDEN_IMPORTS: Set[str] = {
    'os',
    'sys', 
    'subprocess',
    'shutil',
    'pathlib',  # Can be used for path traversal
    'socket',
    'requests',
    'urllib',
    'http',
    'ftplib',
    'smtplib',
    'pickle',   # Arbitrary code execution via deserialization
    'marshal',
    'shelve',
    'ctypes',   # Direct memory access
    'multiprocessing',
    'threading',  # Can spawn uncontrolled processes
}

# Allowed exceptions (safe subsets)
ALLOWED_IMPORTS: Set[str] = {
    'math',
    'random',
    'numpy',
    'matplotlib',
    'matplotlib.pyplot',
    'pandas',
    'json',
    'csv',
    'datetime',
    'collections',
    'itertools',
    'functools',
    'typing',
    're',
    'string',
    'decimal',
    'fractions',
    'statistics',
    'scipy',
    'seaborn',
    'PIL',
    'PIL.Image',
}

# Forbidden attribute access patterns
FORBIDDEN_ATTRS: Set[str] = {
    'eval',
    'exec',
    'compile',
    '__import__',
    'globals',
    'locals',
    'getattr',
    'setattr',
    'delattr',
    'open',  # File operations outside sandbox
    'system',
    'popen',
    'spawn',
    'fork',
    'remove',
    'unlink',
    'rmdir',
    'rmtree',
}

# Dangerous string patterns (path traversal, system paths)
DANGEROUS_PATTERNS: List[str] = [
    '../',
    '..\\',
    '/etc/',
    '/root/',
    '/home/',
    'C:\\Windows',
    'C:\\System',
    'C:\\Users\\',  # Outside sandbox
    '/usr/bin',
    '/bin/',
    'cmd.exe',
    'powershell',
]


class SafetyVisitor(ast.NodeVisitor):
    """
    AST visitor that walks the code tree and flags violations.
    
    Educational Note:
    -----------------
    ast.NodeVisitor has methods like visit_Import, visit_Call, etc.
    Each method is called when that node type is encountered.
    We override these to check for forbidden patterns.
    """
    
    def __init__(self):
        self.violations: List[str] = []
        self.imports_found: Set[str] = set()
        
    def visit_Import(self, node: ast.Import):
        """Check: import os, import subprocess"""
        for alias in node.names:
            module = alias.name.split('.')[0]
            self.imports_found.add(module)
            if module in FORBIDDEN_IMPORTS and alias.name not in ALLOWED_IMPORTS:
                self.violations.append(
                    f"FORBIDDEN_IMPORT: '{alias.name}' at line {node.lineno}"
                )
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Check: from os import path, from subprocess import run"""
        if node.module:
            root_module = node.module.split('.')[0]
            self.imports_found.add(root_module)
            
            # Check if full module path is allowed
            if node.module in ALLOWED_IMPORTS:
                self.generic_visit(node)
                return
                
            if root_module in FORBIDDEN_IMPORTS:
                self.violations.append(
                    f"FORBIDDEN_IMPORT: 'from {node.module}' at line {node.lineno}"
                )
        self.generic_visit(node)
        
    def visit_Call(self, node: ast.Call):
        """Check: eval(), exec(), os.system()"""
        # Direct calls like eval(...)
        if isinstance(node.func, ast.Name):
            if node.func.id in FORBIDDEN_ATTRS:
                self.violations.append(
                    f"FORBIDDEN_CALL: '{node.func.id}()' at line {node.lineno}"
                )
        # Attribute calls like os.system(...)
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in FORBIDDEN_ATTRS:
                self.violations.append(
                    f"FORBIDDEN_ATTR_CALL: '.{node.func.attr}()' at line {node.lineno}"
                )
        self.generic_visit(node)
        
    def visit_Constant(self, node: ast.Constant):
        """Check string literals for path traversal patterns."""
        if isinstance(node.value, str):
            for pattern in DANGEROUS_PATTERNS:
                if pattern.lower() in node.value.lower():
                    self.violations.append(
                        f"DANGEROUS_PATH: '{pattern}' found in string at line {node.lineno}"
                    )
                    break  # One violation per string
        self.generic_visit(node)


def scan_code(code: str) -> ShieldResult:
    """
    Main entry point: scan code string for safety violations.
    
    Returns:
        ShieldResult with safe=True if no violations found.
        
    Educational Note:
    -----------------
    1. Parse code into AST (fails if syntax error)
    2. Walk tree with SafetyVisitor
    3. Collect all violations
    4. Calculate risk score
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return ShieldResult(
            safe=False,
            violations=[f"SYNTAX_ERROR: {e}"],
            risk_score=0.5  # Syntax errors are suspicious but not critical
        )
    
    visitor = SafetyVisitor()
    visitor.visit(tree)
    
    # Calculate risk score based on violation severity
    risk_score = 0.0
    for v in visitor.violations:
        if 'FORBIDDEN_IMPORT' in v:
            risk_score += 0.4
        elif 'FORBIDDEN_CALL' in v:
            risk_score += 0.5
        elif 'DANGEROUS_PATH' in v:
            risk_score += 0.3
        else:
            risk_score += 0.2
    
    risk_score = min(risk_score, 1.0)  # Cap at 1.0
    
    return ShieldResult(
        safe=len(visitor.violations) == 0,
        violations=visitor.violations,
        risk_score=risk_score
    )


def shield_gate(code: str) -> Tuple[bool, str]:
    """
    Simple gate function for integration with sandbox.
    
    Returns:
        (True, "CLEAR") if safe
        (False, "BLOCKED: ...reasons...") if unsafe
    """
    result = scan_code(code)
    
    if result.safe:
        return True, "CLEAR"
    else:
        reasons = "; ".join(result.violations[:5])  # Limit to 5
        return False, f"BLOCKED [risk={result.risk_score:.2f}]: {reasons}"


# Quick self-test
if __name__ == "__main__":
    print("=== AST Shield Self-Test ===\n")
    
    # Safe code
    safe_code = '''
import numpy as np
import matplotlib.pyplot as plt
x = np.linspace(0, 10, 100)
plt.plot(x, np.sin(x))
plt.savefig("output.png")
'''
    
    # Dangerous code
    danger_code = '''
import os
import subprocess
os.system("rm -rf /")
eval(user_input)
path = "../../../etc/passwd"
'''
    
    print("Testing SAFE code:")
    result = scan_code(safe_code)
    print(f"  Safe: {result.safe}, Risk: {result.risk_score}")
    
    print("\nTesting DANGEROUS code:")
    result = scan_code(danger_code)
    print(f"  Safe: {result.safe}, Risk: {result.risk_score}")
    for v in result.violations:
        print(f"    - {v}")

