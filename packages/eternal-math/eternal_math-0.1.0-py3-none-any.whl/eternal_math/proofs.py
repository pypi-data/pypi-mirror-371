"""
Mathematical proof system and logical frameworks.
"""

from typing import List, Dict, Any, Optional, Callable
from abc import ABC, abstractmethod


class Statement(ABC):
    """Abstract base class for mathematical statements."""
    
    def __init__(self, description: str):
        self.description = description
    
    @abstractmethod
    def evaluate(self, context: Dict[str, Any] = None) -> bool:
        """Evaluate the truth value of the statement."""
        pass
    
    def __repr__(self):
        return f"Statement({self.description})"


class Axiom(Statement):
    """A mathematical axiom - a statement assumed to be true."""
    
    def evaluate(self, context: Dict[str, Any] = None) -> bool:
        return True  # Axioms are always true by definition


class Theorem(Statement):
    """A mathematical theorem with a proof."""
    
    def __init__(self, description: str, proof: Optional['Proof'] = None):
        super().__init__(description)
        self.proof = proof
        self.proven = proof is not None
    
    def evaluate(self, context: Dict[str, Any] = None) -> bool:
        return self.proven and (self.proof.verify() if self.proof else False)


class Proof:
    """A mathematical proof consisting of steps and logical deductions."""
    
    def __init__(self, theorem: Theorem, steps: List['ProofStep'] = None):
        self.theorem = theorem
        self.steps = steps or []
        self.axioms = []
        self.assumptions = []
    
    def add_step(self, step: 'ProofStep'):
        """Add a proof step."""
        self.steps.append(step)
    
    def add_axiom(self, axiom: Axiom):
        """Add an axiom to the proof."""
        self.axioms.append(axiom)
    
    def add_assumption(self, assumption: Statement):
        """Add an assumption to the proof."""
        self.assumptions.append(assumption)
    
    def verify(self) -> bool:
        """Verify the validity of the proof."""
        # Basic verification: check if all steps are valid
        context = {}
        
        # All axioms are true
        for axiom in self.axioms:
            context[axiom.description] = True
        
        # Assumptions are taken as true for the proof
        for assumption in self.assumptions:
            context[assumption.description] = True
        
        # Verify each step
        for step in self.steps:
            if not step.verify(context):
                return False
            # Add the conclusion of this step to context
            context[step.conclusion.description] = True
        
        return True


class ProofStep:
    """A single step in a mathematical proof."""
    
    def __init__(self, 
                 premises: List[Statement], 
                 conclusion: Statement, 
                 rule: str,
                 justification: str = ""):
        self.premises = premises
        self.conclusion = conclusion
        self.rule = rule  # The logical rule used (e.g., "Modus Ponens", "Direct Proof")
        self.justification = justification
    
    def verify(self, context: Dict[str, Any]) -> bool:
        """Verify this proof step is valid."""
        # Check if all premises are true in the current context
        for premise in self.premises:
            if premise.description not in context or not context[premise.description]:
                return False
        
        # For now, we assume if premises are true and we have a rule, conclusion follows
        # In a more sophisticated system, we'd have rule-specific verification
        return True


class DirectProof(Proof):
    """A direct proof: assume P, show Q."""
    
    def __init__(self, theorem: Theorem, assumption: Statement):
        super().__init__(theorem)
        self.add_assumption(assumption)


class ProofByContradiction(Proof):
    """A proof by contradiction: assume ¬Q, derive contradiction."""
    
    def __init__(self, theorem: Theorem, negated_conclusion: Statement):
        super().__init__(theorem)
        self.negated_conclusion = negated_conclusion
        self.add_assumption(negated_conclusion)


# Common mathematical statements
class EqualityStatement(Statement):
    """Statement asserting equality between two expressions."""
    
    def __init__(self, left: Any, right: Any):
        self.left = left
        self.right = right
        super().__init__(f"{left} = {right}")
    
    def evaluate(self, context: Dict[str, Any] = None) -> bool:
        return self.left == self.right


class InequalityStatement(Statement):
    """Statement asserting inequality between two expressions."""
    
    def __init__(self, left: Any, right: Any, operator: str):
        self.left = left
        self.right = right
        self.operator = operator
        super().__init__(f"{left} {operator} {right}")
    
    def evaluate(self, context: Dict[str, Any] = None) -> bool:
        if self.operator == "<":
            return self.left < self.right
        elif self.operator == ">":
            return self.left > self.right
        elif self.operator == "<=":
            return self.left <= self.right
        elif self.operator == ">=":
            return self.left >= self.right
        return False


class LogicalStatement(Statement):
    """A general logical statement that can be evaluated as true/false."""
    
    def __init__(self, description: str, truth_value: bool = True):
        self.truth_value = truth_value
        super().__init__(description)
    
    def evaluate(self, context: Dict[str, Any] = None) -> bool:
        return self.truth_value


__all__ = [
    'Statement', 'Axiom', 'Theorem', 'Proof', 'ProofStep',
    'DirectProof', 'ProofByContradiction', 
    'EqualityStatement', 'InequalityStatement', 'LogicalStatement'
]
