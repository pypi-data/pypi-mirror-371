# aegis/core/compliance.py

from typing import Dict, List

class ComplianceMapper:
    """
    Maps Aegis evaluation categories to common AI regulatory and compliance frameworks.
    This provides a direct link between a technical test and a governance control.
    """

    # This is a foundational mapping. It can be expanded with more detail and frameworks over time.
    FRAMEWORK_MAP: Dict[str, Dict[str, List[str]]] = {
        "NIST_AI_RMF": {
            "Data_Exfiltration": ["GOVERN-3 (Data Privacy)", "MAP-5 (System Security)", "MEASURE-2 (Vulnerability Monitoring)"],
            "Code_Generation_Exploits": ["MAP-1 (System Purpose)", "MAP-5 (System Security)", "MEASURE-2 (Vulnerability Monitoring)"],
            "Bias_Harmful_Content": ["MAP-2 (System Bias)", "MEASURE-2.3 (Fairness Metrics)"],
            "Indirect_Prompt_Injection": ["MAP-1.3 (System Boundaries)", "MEASURE-2.1 (Input Validation)"],
            "Direct_Prompt_Injection": ["MAP-1.3 (System Boundaries)", "MEASURE-2.1 (Input Validation)"],
        },
        "EU_AI_ACT": {
            "Data_Exfiltration": ["Article 10 (Data Governance)", "Article 15 (Accuracy, Robustness, Cybersecurity)"],
            "Code_Generation_Exploits": ["Article 15 (Accuracy, Robustness, Cybersecurity)"],
            "Bias_Harmful_Content": ["Article 10 (Data Governance)", "Article 9 (Risk Management System)"],
            "Indirect_Prompt_Injection": ["Article 15 (Accuracy, Robustness, Cybersecurity)"],
            "Direct_Prompt_Injection": ["Article 15 (Accuracy, Robustness, Cybersecurity)"],
        }
    }

    @classmethod
    def get_mappings_for_category(cls, category: str) -> Dict[str, List[str]]:
        """
        Retrieves all compliance mappings for a given Aegis test category.
        
        Args:
            category (str): The category of the adversarial prompt.
            
        Returns:
            Dict[str, List[str]]: A dictionary where keys are framework names and
                                 values are lists of relevant control identifiers.
        """
        mappings = {}
        for framework, categories in cls.FRAMEWORK_MAP.items():
            if category in categories:
                mappings[framework] = categories[category]
        return mappings
