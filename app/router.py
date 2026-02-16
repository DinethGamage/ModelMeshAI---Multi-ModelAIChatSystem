"""
Intelligent Router for dynamic model selection.
Implements hybrid routing: rule-based + LLM-based classification.
"""

import re
import json
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

from app.models import model_manager
from app.session import Session


@dataclass
class RouteDecision:
    """Represents a routing decision with metadata."""
    category: str  # math, coding, writing, document, general
    model_type: str  # Model to use (general, code, math, document)
    confidence: float  # Confidence in the decision (0-1)
    reasoning: str  # Explanation of routing decision
    method: str  # "rule-based" or "llm-based"


class IntelligentRouter:
    """
    Hybrid intelligent router that selects appropriate model based on query type.
    Uses rule-based detection first, falls back to LLM classification.
    """
    
    # Keywords for rule-based detection
    MATH_KEYWORDS = {
        'calculate', 'compute', 'solve', 'equation', 'sum', 'multiply', 
        'divide', 'subtract', 'add', 'percentage', 'average', 'mean',
        'integral', 'derivative', 'algebra', 'geometry', 'math'
    }
    
    CODE_KEYWORDS = {
        'code', 'program', 'function', 'class', 'implement', 'algorithm',
        'debug', 'python', 'javascript', 'java', 'c++', 'sql', 'api',
        'variable', 'loop', 'array', 'syntax', 'compile', 'execute'
    }
    
    WRITING_KEYWORDS = {
        'write', 'compose', 'draft', 'essay', 'letter', 'email',
        'story', 'article', 'blog', 'poem', 'paragraph', 'rewrite',
        'paraphrase', 'summarize', 'creative', 'narrative'
    }
    
    DOCUMENT_KEYWORDS = {
        'document', 'pdf', 'uploaded', 'file', 'according to',
        'based on the', 'in the document', 'from the file'
    }
    
    # Regex patterns for detection
    MATH_PATTERNS = [
        r'\d+\s*[\+\-\*\/\^]\s*\d+',  # Basic arithmetic
        r'\d+\s*%',  # Percentages
        r'=\s*\?',  # Equations
        r'\b\d+(?:\.\d+)?\b.*\b\d+(?:\.\d+)?\b',  # Two or more numbers
    ]
    
    CODE_PATTERNS = [
        r'```[\w]*',  # Code blocks
        r'def\s+\w+\(',  # Python functions
        r'function\s+\w+\(',  # JavaScript functions
        r'class\s+\w+',  # Class definitions
        r'import\s+\w+',  # Import statements
        r'<\w+>.*</\w+>',  # HTML/XML tags
    ]
    
    def __init__(self):
        """Initialize the intelligent router."""
        self.classification_model = model_manager.get_classification_model()
    
    def _detect_by_rules(self, query: str, session: Session) -> Optional[RouteDecision]:
        """
        Attempt to classify query using rule-based patterns.
        
        Args:
            query: User query
            session: Current session (for document context)
            
        Returns:
            RouteDecision if confident, None otherwise
        """
        query_lower = query.lower()
        
        # Check for code patterns first (high specificity)
        for pattern in self.CODE_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return RouteDecision(
                    category="coding",
                    model_type="code",
                    confidence=0.9,
                    reasoning="Detected code syntax or programming patterns",
                    method="rule-based"
                )
        
        # Check for math patterns
        for pattern in self.MATH_PATTERNS:
            if re.search(pattern, query):
                return RouteDecision(
                    category="math",
                    model_type="math",
                    confidence=0.85,
                    reasoning="Detected mathematical expressions or calculations",
                    method="rule-based"
                )
        
        # Check for document keywords (if document uploaded)
        if session.document_uploaded:
            doc_keyword_count = sum(1 for kw in self.DOCUMENT_KEYWORDS if kw in query_lower)
            if doc_keyword_count >= 1:
                return RouteDecision(
                    category="document",
                    model_type="document",
                    confidence=0.85,
                    reasoning="Query references uploaded document context",
                    method="rule-based"
                )
        
        # Check keyword densities
        words = set(query_lower.split())
        
        math_score = len(words & self.MATH_KEYWORDS)
        code_score = len(words & self.CODE_KEYWORDS)
        writing_score = len(words & self.WRITING_KEYWORDS)
        
        # Require multiple keyword matches for confidence
        if math_score >= 2:
            return RouteDecision(
                category="math",
                model_type="math",
                confidence=0.75,
                reasoning=f"Multiple math-related keywords detected ({math_score} keywords)",
                method="rule-based"
            )
        
        if code_score >= 2:
            return RouteDecision(
                category="coding",
                model_type="code",
                confidence=0.75,
                reasoning=f"Multiple programming-related keywords detected ({code_score} keywords)",
                method="rule-based"
            )
        
        if writing_score >= 2:
            return RouteDecision(
                category="writing",
                model_type="general",
                confidence=0.70,
                reasoning=f"Multiple writing-related keywords detected ({writing_score} keywords)",
                method="rule-based"
            )
        
        # Not confident enough - return None to trigger LLM classification
        return None
    
    def _classify_with_llm(self, query: str, session: Session) -> RouteDecision:
        """
        Classify query using LLM when rules are insufficient.
        
        Args:
            query: User query
            session: Current session
            
        Returns:
            RouteDecision from LLM classification
        """
        doc_context = ""
        if session.document_uploaded:
            doc_context = f"Note: User has uploaded document '{session.document_name}'."
        
        classification_prompt = f"""Classify the following user query into exactly ONE category:

Categories:
- math: Mathematical calculations, equations, numerical problems
- coding: Programming, code implementation, debugging, algorithms
- writing: Creative writing, essays, content generation, rewriting
- document: Questions about uploaded documents or files
- general: General conversation, questions, chitchat

{doc_context}

User Query: "{query}"

Respond ONLY with a JSON object in this format:
{{"category": "...", "confidence": 0.0-1.0, "reasoning": "..."}}"""
        
        try:
            response = self.classification_model.invoke(classification_prompt)
            response_text = response.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(response_text)
            
            category = result.get("category", "general")
            confidence = float(result.get("confidence", 0.5))
            reasoning = result.get("reasoning", "LLM classification")
            
            # Map category to model type
            model_map = {
                "math": "math",
                "coding": "code",
                "writing": "general",
                "document": "document",
                "general": "general"
            }
            
            model_type = model_map.get(category, "general")
            
            return RouteDecision(
                category=category,
                model_type=model_type,
                confidence=confidence,
                reasoning=reasoning,
                method="llm-based"
            )
            
        except Exception as e:
            # Fallback to general if classification fails
            return RouteDecision(
                category="general",
                model_type="general",
                confidence=0.5,
                reasoning=f"Classification error, using general model: {str(e)}",
                method="llm-based"
            )
    
    def classify(self, query: str, session: Session) -> RouteDecision:
        """
        Classify a query using hybrid approach.
        
        Args:
            query: User query
            session: Current session
            
        Returns:
            RouteDecision with category and model selection
        """
        # Try rule-based detection first
        rule_decision = self._detect_by_rules(query, session)
        
        if rule_decision and rule_decision.confidence >= 0.7:
            return rule_decision
        
        # Fall back to LLM classification
        llm_decision = self._classify_with_llm(query, session)
        
        # If we had low-confidence rule decision, prefer it if LLM confidence is also low
        if rule_decision and llm_decision.confidence < 0.7:
            return rule_decision if rule_decision.confidence > llm_decision.confidence else llm_decision
        
        return llm_decision
    
    def route(self, query: str, session: Session) -> Tuple[RouteDecision, Dict[str, Any]]:
        """
        Route a query to appropriate handler and return metadata.
        
        Args:
            query: User query
            session: Current session
            
        Returns:
            Tuple of (RouteDecision, routing_metadata)
        """
        decision = self.classify(query, session)
        
        metadata = {
            "route_category": decision.category,
            "model_used": decision.model_type,
            "routing_reason": decision.reasoning,
            "routing_method": decision.method,
            "confidence": decision.confidence
        }
        
        return decision, metadata


# Global router instance
intelligent_router = IntelligentRouter()
