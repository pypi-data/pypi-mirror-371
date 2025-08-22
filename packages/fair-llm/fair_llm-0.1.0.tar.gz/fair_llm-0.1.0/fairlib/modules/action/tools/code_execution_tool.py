# fairlib.modules.action/tools/code_execution_tool.py
"""
================================================================================
                        Code Execution Tool
================================================================================

**Purpose:**
This module provides a tool for executing student code against a set of unit
tests. It is a critical component for assessing the correctness of programming
assignments.

--------------------------------------------------------------------------------

**CRITICAL SECURITY WARNING: SANDBOXING REQUIRED**

The function `sandbox_code_execution` in this module is a **NON-SECURE
PLACEHOLDER**. It uses Python's built-in `subprocess` module, which **DOES NOT**
provide sufficient isolation to safely run untrusted code. A malicious submission
could potentially escape the subprocess and harm the host system.

For any real-world or production use, this function **MUST BE REPLACED** with a
robust sandboxing technology. Options include:
  - **Docker Containers:** Running each submission in a new, ephemeral, and
    network-isolated container.
  - **MicroVMs (gVisor, Firecracker):** Providing stronger kernel-level isolation.
  - **Third-Party Secure Code Execution APIs.**

**DO NOT USE THIS TOOL IN A PRODUCTION ENVIRONMENT AS-IS.**
--------------------------------------------------------------------------------
"""
import json
import logging
import subprocess
import sys
from pathlib import Path
from fairlib import AbstractTool

logger = logging.getLogger(__name__)

def sandbox_code_execution(code: str, tests: str) -> str:
    """
    Executes student code against unit tests in a sandboxed environment.
    **WARNING: THIS IS A NON-SECURE PLACEHOLDER IMPLEMENTATION.**
    """
    logger.warning("Executing code in a NON-SECURE sandbox. For demonstration purposes only.")
    temp_student_code_file = Path("temp_student_code.py")
    temp_tests_file = Path("temp_tests.py")
    try:
        # Write student code and test code to temporary files. This is a common
        # pattern for command-line test runners like pytest.
        temp_student_code_file.write_text(code, encoding='utf-8')
        
        # Modify the test file to import from the temp student file name.
        # This assumes a convention in the test file, e.g., `from student_code import ...`
        # which we replace with `from temp_student_code import ...`
        modified_test_code = tests.replace("from student_code", "from temp_student_code")
        temp_tests_file.write_text(modified_test_code, encoding='utf-8')
        
        # Construct the command to run pytest.
        command = [sys.executable, "-m", "pytest", str(temp_tests_file)]
        
        # Execute the command in a subprocess with a timeout.
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        
        # Return the formatted output from the test runner.
        return f"Pytest Output:\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"

    except subprocess.TimeoutExpired:
        logger.error("Code execution timed out after 30 seconds.")
        return "Error: Code execution timed out after 30 seconds. The code may contain an infinite loop."
    except FileNotFoundError:
        logger.error("Pytest not found. Please ensure 'pytest' is installed in the execution environment ('pip install pytest').")
        return "Error: The 'pytest' library is not installed or not in the system's PATH."
    except Exception as e:
        logger.error(f"Sandbox execution failed with an unexpected error: {e}", exc_info=True)
        return f"Error: An unexpected error occurred during code execution: {e}"
    finally:
        # A crucial step: ensure temporary files are always deleted, even if an error occurs.
        if temp_student_code_file.exists(): temp_student_code_file.unlink()
        if temp_tests_file.exists(): temp_tests_file.unlink()

class CodeExecutionTool(AbstractTool):
    """A tool that allows an agent to execute student code against unit tests."""
    name = "run_code_with_tests"
    description = "Executes a student's Python code against pytest unit tests in a sandbox and returns the results."
    
    def use(self, tool_input: str) -> str:
        """
        Parses input and calls the sandboxed execution function.
        
        Args:
            tool_input: A JSON string containing 'student_code' and 'test_code'.

        Returns:
            The output from the code execution sandbox.
        """
        try:
            data = json.loads(tool_input)
            # This delegation is where the actual code execution happens.
            return sandbox_code_execution(data['student_code'], data['test_code'])
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Invalid input format for CodeExecutionTool: {e}")
            return f"Error: Invalid input format. Expected JSON with 'student_code' and 'test_code' keys. Details: {e}"