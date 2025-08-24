"""
Example: Enhanced Proof System Demonstration

This example showcases the enhanced proof system with detailed proof steps
for the Fundamental Theorem of Arithmetic.
"""

from eternal_math import create_fundamental_theorem_of_arithmetic


def main():
    """Demonstrate the enhanced proof system capabilities."""
    print("=== Eternal Math: Enhanced Proof System ===\n")
    
    # Create the Fundamental Theorem of Arithmetic with detailed proof
    theorem = create_fundamental_theorem_of_arithmetic()
    
    print("THEOREM:")
    print(f"  {theorem.description}\n")
    
    print(f"PROOF STATUS: {'Proven' if theorem.proven else 'Not proven'}")
    print(f"PROOF VERIFICATION: {'Valid' if theorem.evaluate() else 'Invalid'}\n")
    
    if theorem.proof:
        print("AXIOMS USED:")
        for i, axiom in enumerate(theorem.proof.axioms, 1):
            print(f"  {i}. {axiom.description}")
        
        print(f"\nPROOF STEPS ({len(theorem.proof.steps)} total):")
        for i, step in enumerate(theorem.proof.steps, 1):
            print(f"\n  Step {i}: {step.rule}")
            print(f"    Conclusion: {step.conclusion.description}")
            print(f"    Justification: {step.justification}")
            if step.premises:
                print(f"    Based on: {len(step.premises)} premise(s)")
        
        print(f"\nPROOF VERIFICATION:")
        verification_result = theorem.proof.verify()
        print(f"  All steps valid: {verification_result}")
        print(f"  Logical structure: {'Sound' if verification_result else 'Unsound'}")
    
    print("\n" + "="*60)
    print("This demonstrates how Eternal Math can:")
    print("• Create formal mathematical theorems")
    print("• Build structured proofs with logical steps")
    print("• Verify proof validity automatically")  
    print("• Combine axioms, premises, and conclusions")
    print("• Support various proof techniques (induction, contradiction)")
    print("="*60)


if __name__ == "__main__":
    main()
