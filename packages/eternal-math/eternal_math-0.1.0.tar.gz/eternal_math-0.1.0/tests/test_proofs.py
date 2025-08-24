"""
Test suite for the proof system and theorem verification.
"""

import pytest
from eternal_math.proofs import (
    Axiom, Theorem, Proof, ProofStep, LogicalStatement,
    EqualityStatement, InequalityStatement
)
from eternal_math.number_theory import create_fundamental_theorem_of_arithmetic


class TestProofSystem:
    """Test the basic proof system components."""
    
    def test_axiom_creation(self):
        """Test axiom creation and evaluation."""
        axiom = Axiom("Every integer has a unique prime factorization")
        assert axiom.evaluate() is True
        assert "unique prime factorization" in axiom.description
    
    def test_logical_statement(self):
        """Test logical statement creation and evaluation."""
        stmt_true = LogicalStatement("2 is prime", True)
        stmt_false = LogicalStatement("4 is prime", False)
        
        assert stmt_true.evaluate() is True
        assert stmt_false.evaluate() is False
        assert "2 is prime" in stmt_true.description
        assert "4 is prime" in stmt_false.description
    
    def test_equality_statement(self):
        """Test equality statement evaluation."""
        eq_true = EqualityStatement(2 + 2, 4)
        eq_false = EqualityStatement(2 + 2, 5)
        
        assert eq_true.evaluate() is True
        assert eq_false.evaluate() is False
        assert "4 = 4" in eq_true.description
        assert "4 = 5" in eq_false.description
    
    def test_inequality_statement(self):
        """Test inequality statement evaluation."""
        ineq_lt = InequalityStatement(3, 5, "<")
        ineq_gt = InequalityStatement(7, 2, ">")
        ineq_false = InequalityStatement(5, 3, "<")
        
        assert ineq_lt.evaluate() is True
        assert ineq_gt.evaluate() is True
        assert ineq_false.evaluate() is False
    
    def test_theorem_without_proof(self):
        """Test theorem creation without proof."""
        theorem = Theorem("Pythagorean theorem")
        assert theorem.proven is False
        assert theorem.evaluate() is False
    
    def test_theorem_with_proof(self):
        """Test theorem creation with proof."""
        theorem = Theorem("Simple theorem")
        proof = Proof(theorem)
        proof.add_axiom(Axiom("Basic axiom"))
        
        theorem.proof = proof
        theorem.proven = True
        
        assert theorem.proven is True
        assert theorem.evaluate() is True


class TestProofSteps:
    """Test proof step creation and verification."""
    
    def test_proof_step_creation(self):
        """Test creating proof steps."""
        premise = LogicalStatement("P implies Q")
        conclusion = LogicalStatement("Q")
        
        step = ProofStep(
            premises=[premise],
            conclusion=conclusion,
            rule="Modus Ponens",
            justification="Basic logical inference"
        )
        
        assert len(step.premises) == 1
        assert step.rule == "Modus Ponens"
        assert "Basic logical inference" in step.justification
    
    def test_proof_step_verification(self):
        """Test proof step verification logic."""
        premise = LogicalStatement("All men are mortal")
        conclusion = LogicalStatement("Socrates is mortal")
        
        step = ProofStep(
            premises=[premise],
            conclusion=conclusion,
            rule="Universal Instantiation"
        )
        
        # Context where premise is true
        context = {premise.description: True}
        assert step.verify(context) is True
        
        # Context where premise is false
        context_false = {premise.description: False}
        assert step.verify(context_false) is False


class TestFundamentalTheoremProof:
    """Test the enhanced Fundamental Theorem of Arithmetic proof."""
    
    def test_theorem_creation(self):
        """Test that the theorem is properly created."""
        theorem = create_fundamental_theorem_of_arithmetic()
        
        assert theorem is not None
        assert theorem.proven is True
        assert theorem.proof is not None
        assert "product of prime numbers" in theorem.description
    
    def test_proof_structure(self):
        """Test the proof structure and components."""
        theorem = create_fundamental_theorem_of_arithmetic()
        proof = theorem.proof
        
        # Check axioms
        assert len(proof.axioms) == 3
        axiom_descriptions = [axiom.description for axiom in proof.axioms]
        assert any("smallest divisor" in desc for desc in axiom_descriptions)
        assert any("prime" in desc for desc in axiom_descriptions)
        
        # Check proof steps
        assert len(proof.steps) == 9
        
        # Verify step types and rules
        rules = [step.rule for step in proof.steps]
        assert "Case Analysis" in rules
        assert "Strong Induction" in rules
        assert "Proof by Contradiction Setup" in rules
        assert "Conjunction" in rules
    
    def test_proof_verification(self):
        """Test that the proof can be verified."""
        theorem = create_fundamental_theorem_of_arithmetic()
        proof = theorem.proof
        
        # The proof should verify successfully
        assert proof.verify() is True
    
    def test_proof_step_justifications(self):
        """Test that all proof steps have justifications."""
        theorem = create_fundamental_theorem_of_arithmetic()
        proof = theorem.proof
        
        for i, step in enumerate(proof.steps):
            assert len(step.justification) > 0, f"Step {i+1} lacks justification"
            assert isinstance(step.justification, str)
    
    def test_theorem_evaluation(self):
        """Test that the theorem evaluates as true."""
        theorem = create_fundamental_theorem_of_arithmetic()
        assert theorem.evaluate() is True


class TestProofIntegration:
    """Test integration between different proof components."""
    
    def test_complete_proof_workflow(self):
        """Test a complete proof workflow from axioms to theorem."""
        # Create a simple theorem: "If P then Q, P is true, therefore Q is true"
        theorem = Theorem("Modus Ponens Example")
        proof = Proof(theorem)
        
        # Add axioms
        axiom1 = Axiom("If it rains, then the ground gets wet")
        axiom2 = Axiom("It is raining")
        proof.add_axiom(axiom1)
        proof.add_axiom(axiom2)
        
        # Add proof step
        conclusion = LogicalStatement("The ground gets wet")
        step = ProofStep(
            premises=[axiom1, axiom2],
            conclusion=conclusion,
            rule="Modus Ponens",
            justification="From 'If P then Q' and 'P', we can conclude 'Q'"
        )
        proof.add_step(step)
        
        # Complete the theorem
        theorem.proof = proof
        theorem.proven = True
        
        # Verify everything works
        assert proof.verify() is True
        assert theorem.evaluate() is True
        assert len(proof.steps) == 1
        assert len(proof.axioms) == 2


if __name__ == "__main__":
    pytest.main([__file__])
