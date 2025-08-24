# aegis/core/models.py

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

class Classification(Enum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    PARTIAL_COMPLIANCE = "PARTIAL_COMPLIANCE"
    ERROR = "ERROR"
    AMBIGUOUS = "AMBIGUOUS"

@dataclass
class MultiModalInput:
    """A flexible container for multi-modal data."""
    media_type: str  # e.g., 'image/jpeg', 'audio/wav'
    data: bytes

@dataclass
class AdversarialPrompt:
    id: str
    category: str
    subcategory: str
    severity: str
    prompt_text: str
    expected_behavior: str
    success_indicators: List[str] = field(default_factory=list)
    failure_indicators: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    multi_modal_data: List[MultiModalInput] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Converts the dataclass instance to a dictionary for display."""
        return {
            "id": self.id,
            "category": self.category,
            "subcategory": self.subcategory,
            "severity": self.severity,
            "prompt_text": self.prompt_text,
            "expected_behavior": self.expected_behavior,
            "success_indicators": self.success_indicators,
            "failure_indicators": self.failure_indicators,
            "tags": self.tags,
        }

@dataclass
class ModelResponse:
    output_text: str
    prompt_id: str
    model_name: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

@dataclass
class AnalysisResult:
    classification: Classification
    explanation: str
    aegis_risk_score: float
