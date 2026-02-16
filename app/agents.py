"""
Agent tools and utilities for specialized tasks.
Provides calculator tool with LLM-based decision making.
"""

import re
import json
from typing import Dict, Any, Optional
from app.models import model_manager


class CalculatorTool:
    """Calculator tool for mathematical operations."""
    
    @staticmethod
    def calculate(expression: str) -> float:
        """
        Safely evaluate a mathematical expression.
        
        Args:
            expression: Mathematical expression as string
            
        Returns:
            Calculated result
            
        Raises:
            ValueError: If expression is invalid
        """
        # Clean the expression
        expression = expression.strip()
        
        # Only allow safe mathematical operations
        allowed_chars = set("0123456789+-*/().,. ")
        if not all(c in allowed_chars for c in expression):
            raise ValueError(f"Invalid characters in expression: {expression}")
        
        try:
            # Replace common math notation
            expression = expression.replace("^", "**")
            expression = expression.replace("÷", "/")
            expression = expression.replace("×", "*")
            
            # Evaluate safely
            result = eval(expression, {"__builtins__": {}}, {})
            return float(result)
        except Exception as e:
            raise ValueError(f"Cannot evaluate expression '{expression}': {str(e)}")
    
    @staticmethod
    def get_tool_description() -> str:
        """Get description of the calculator tool for LLM."""
        return """
Calculator Tool:
- Use this tool to perform precise mathematical calculations
- Supports: addition (+), subtraction (-), multiplication (*), division (/), parentheses ()
- Example: To calculate 25 * 4 + 10, use calculator("25 * 4 + 10")
- Returns exact numerical result
"""


class MathAgent:
    """Agent that can use calculator tool for mathematical queries."""
    
    def __init__(self):
        """Initialize the math agent."""
        self.calculator = CalculatorTool()
        self.model = model_manager.get_model("math")
    
    def _extract_calculation(self, llm_response: str) -> Optional[str]:
        """
        Extract calculation expression from LLM response.
        
        Args:
            llm_response: Response from LLM
            
        Returns:
            Mathematical expression or None
        """
        # Look for calculator function calls
        patterns = [
            r'calculator\(["\'](.+?)["\']\)',
            r'calculate\(["\'](.+?)["\']\)',
            r'CALCULATE:\s*(.+?)(?:\n|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, llm_response, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def solve(self, query: str) -> Dict[str, Any]:
        """
        Solve a mathematical query using LLM and calculator tool.
        
        Args:
            query: User's mathematical query
            
        Returns:
            Dictionary with answer and tool usage information
        """
        # Create system prompt with tool description
        system_prompt = f"""You are a mathematical assistant with access to a calculator tool.
        
{self.calculator.get_tool_description()}

When you need to perform calculations:
1. Use the calculator tool by writing: calculator("expression")
2. Provide the final answer clearly

User query: {query}

If calculation is needed, first show calculator("expression"), then provide the answer.
If you can answer directly (e.g., basic facts), just answer directly.
"""
        
        # Get LLM response
        llm_response = self.model.invoke(query)
        response_text = llm_response.content
        
        # Check if calculator tool was requested
        calculation_expr = self._extract_calculation(response_text)
        
        result = {
            "answer": response_text,
            "tool_used": False,
            "calculation": None,
            "calculation_result": None,
        }
        
        if calculation_expr:
            try:
                calc_result = self.calculator.calculate(calculation_expr)
                result["tool_used"] = True
                result["calculation"] = calculation_expr
                result["calculation_result"] = calc_result
                
                # Generate final answer with calculation result
                final_prompt = f"""Original query: {query}
Calculation performed: {calculation_expr} = {calc_result}

Provide a clear, natural language answer incorporating this result."""
                
                final_response = self.model.invoke(final_prompt)
                result["answer"] = final_response.content
            except ValueError as e:
                result["answer"] = f"I attempted a calculation but encountered an error: {str(e)}. Let me provide an estimate: {response_text}"
        
        return result


# Global math agent instance
math_agent = MathAgent()
