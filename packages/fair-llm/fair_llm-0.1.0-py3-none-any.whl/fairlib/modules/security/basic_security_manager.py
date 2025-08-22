# fairlib.modules.security/basic_security_manager.py
"""
This module provides a basic implementation of the AbstractSecurityManager.
"""
import re
from typing import Any, List, Optional, Pattern

from fairlib.core.interfaces.security import AbstractSecurityManager

# A default list of patterns to detect common prompt injection attempts.
# In a production system, these would be managed in a configuration file.
DEFAULT_PROMPT_INJECTION_PATTERNS: List[Pattern] = [
    re.compile(r"\bignore previous instructions\b", re.IGNORECASE),
    re.compile(r"\bdisregard the above\b", re.IGNORECASE),
    re.compile(r"^(?:translate|say|repeat|ecco|eko|echo)\s+the\s+following\s+text", re.IGNORECASE),
]


class BasicSecurityManager(AbstractSecurityManager):
    """
    A basic implementation of the security manager that validates text inputs
    against a list of regular expression patterns to prevent simple prompt
    injection attacks.

    It also includes a **non-secure** placeholder for code execution.
    """
    def __init__(self, patterns: Optional[List[Pattern]] = None):
        """
        Initializes the BasicSecurityManager.

        Args:
            patterns: An optional list of compiled regular expression patterns
                      to screen for. If None, uses the default list.
        """
        self.validation_patterns = patterns or DEFAULT_PROMPT_INJECTION_PATTERNS
        print("✅ BasicSecurityManager initialized.")

    def validate_input(self, input_data: Any, schema: Optional[dict] = None) -> bool:
        """
        Validates the input text against a set of harmful patterns.

        This implementation focuses on string-based prompt injection. It does not
        currently use the 'schema' parameter.

        Args:
            input_data: The input data to validate.
            schema: An optional schema (ignored in this implementation).

        Returns:
            `True` if the input is considered safe, `False` otherwise.
        """
        # This basic validator only processes string inputs.
        if not isinstance(input_data, str):
            # Non-string input is considered safe by this validator, as it's not a prompt.
            return True

        # Check the input against each configured pattern.
        for pattern in self.validation_patterns:
            if pattern.search(input_data):
                print(f"Validation failed: Detected potentially harmful pattern: {pattern.pattern}")
                return False
        
        # If no patterns are matched, the input is considered valid.
        return True

    def sandbox_code_execution(self, code: str, language: str = "python") -> Any:
        """
        Executes code using Python's built-in `exec`.

        **WARNING**: This method is **NOT SECURE** and should **NOT** be used in
        a production environment. It does not provide a true sandbox and can
        execute arbitrary, potentially malicious code. It is included here only
        to satisfy the interface for demonstration purposes. A real implementation
        should use a secure sandboxing technology like Docker containers or gVisor.
        """
        print("WARNING: Executing code in a non-secure environment.")
        if language.lower() == "python":
            try:
                # Use a dictionary to capture the result of the execution.
                local_scope = {}
                exec(code, globals(), local_scope)
                return local_scope.get('result', 'Execution finished without a "result" variable.')
            except Exception as e:
                return f"Error during execution: {e}"
        else:
            return f"Unsupported language: {language}"

    async def asandbox_code_execution(self, code: str, language: str = "python") -> Any:
        """
        Asynchronously executes code. See the synchronous version for warnings.
        """
        # For this placeholder, the operation is blocking, but we wrap it for
        # async compatibility.
        return self.sandbox_code_execution(code, language)