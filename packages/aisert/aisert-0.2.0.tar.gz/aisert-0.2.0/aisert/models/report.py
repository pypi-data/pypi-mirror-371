class AisertReport:
    """Final validation report containing overall status and detailed results.
    
    Returned by :meth:`Aisert.collect` to provide comprehensive validation outcomes.
    Contains both high-level pass/fail status and granular per-validation details.
    
    :param status: ``True`` if all validations passed, ``False`` if any failed
    :type status: bool
    :param rules: Dictionary mapping execution order to validation results
    :type rules: dict
    
    The ``rules`` dictionary has the format::
    
        {1: {'validator': 'ContainsValidator', 'status': True, 'reason': '...'}}
    
    Example usage::
    
        report = Aisert("Hello world").assert_contains(["Hello"]).collect()
        if report.status:
            print("All validations passed!")
        for order, result in report.rules.items():
            print(f"{order}: {result['validator']} - {result['status']}")
    
    .. versionadded:: 0.1.0
    """

    def __init__(self, status: bool, rules: dict):
        """Create a new validation report.
        
        :param status: Overall validation status (``True`` if all passed)
        :type status: bool
        :param rules: Dictionary of validation results keyed by execution order
        :type rules: dict
        """
        self.status = status
        self.rules = rules

    def __str__(self) -> str:
        """Human-readable string representation of the validation report.
        
        :return: Formatted string showing status and rules summary
        :rtype: str
        """
        return f"Status: {self.status} \n Rules: {self.rules}"
