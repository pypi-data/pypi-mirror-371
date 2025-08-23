"""DSPy modules for Savanty optimization problem solver."""

import dspy
from typing import List, Dict, Any


class ProblemAnalysis(dspy.Signature):
    """Analyze an optimization problem description and extract structured information."""
    
    problem_description = dspy.InputField(desc="Natural language description of an optimization problem")
    analysis = dspy.OutputField(desc="Structured analysis of the problem including domain, variables, constraints, and objective")


class ProblemValidation(dspy.Signature):
    """Validate if a problem description can be converted to a solvable ASP program."""
    
    problem_description = dspy.InputField(desc="Natural language description of an optimization problem")
    is_valid = dspy.OutputField(desc="Boolean indicating if the problem can be solved with ASP")
    reason = dspy.OutputField(desc="Explanation of why the problem is or isn't valid for ASP solving")


class GapIdentification(dspy.Signature):
    """Identify gaps and missing information in an optimization problem description."""
    
    problem_description = dspy.InputField(desc="Natural language description of an optimization problem")
    has_gaps = dspy.OutputField(desc="Boolean indicating if there are gaps in the problem description")
    gaps = dspy.OutputField(desc="List of specific information gaps in the problem description")
    questions = dspy.OutputField(desc="List of questions to ask the user to fill the gaps")


class ProgramGeneration(dspy.Signature):
    """Generate ASP program components from problem analysis."""
    
    analysis = dspy.InputField(desc="Structured analysis of an optimization problem")
    program_components = dspy.OutputField(desc="JSON structure with predicates, facts, constraints, and optimization statement for ASP")


class ProblemRefinement(dspy.Signature):
    """Refine a problem description with additional information."""
    
    original_problem = dspy.InputField(desc="Original problem description")
    additional_info = dspy.InputField(desc="Additional information provided by the user")
    refined_problem = dspy.OutputField(desc="Refined problem description with additional information incorporated")


class InteractiveProblemSolver(dspy.Module):
    """Main module for solving optimization problems using DSPy with interactive gap filling."""
    
    def __init__(self):
        super().__init__()
        self.analyze = dspy.Predict(ProblemAnalysis)
        self.validate = dspy.Predict(ProblemValidation)
        self.identify_gaps = dspy.Predict(GapIdentification)
        self.generate = dspy.Predict(ProgramGeneration)
        self.refine = dspy.Predict(ProblemRefinement)
    
    def forward(self, problem_description: str, additional_info: str = None):
        # If we have additional info, refine the problem first
        if additional_info:
            refinement = self.refine(
                original_problem=problem_description,
                additional_info=additional_info
            )
            problem_description = refinement.refined_problem
        
        # First validate if the problem makes sense for ASP
        validation = self.validate(problem_description=problem_description)
        
        if validation.is_valid.lower() != "true":
            # Check if there are gaps we can ask about
            gap_check = self.identify_gaps(problem_description=problem_description)
            
            if gap_check.has_gaps.lower() == "true":
                # Return the questions to ask the user
                return dspy.Prediction(
                    validation=validation,
                    gap_check=gap_check,
                    needs_more_info=True,
                    questions=gap_check.questions
                )
            else:
                # Problem is invalid and we can't ask for more info
                raise ValueError(f"Problem cannot be solved with ASP: {validation.reason}")
        
        # Analyze the problem
        analysis = self.analyze(problem_description=problem_description)
        
        # Generate program components
        program = self.generate(analysis=analysis.analysis)
        
        return dspy.Prediction(
            validation=validation,
            analysis=analysis,
            program=program,
            needs_more_info=False
        )