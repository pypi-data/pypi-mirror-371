# fairlib.modules.action/tools/grading_tool.py
"""
================================================================================
                    Structured Grading Tools
================================================================================

**Purpose:**
This module provides the specialized tools responsible for the final, most
critical step of the autograding process: generating a structured, JSON-based
grade report.

**How it Works:**
These tools take all the qualitative and quantitative analyses from the other
worker agents (e.g., content analysis, test results, style feedback) and use a
Large Language Model to synthesize them into a single, validated Pydantic
object (`FinalGrade`). This enforces consistency and ensures that every
criterion in the rubric is explicitly addressed.

This module contains two distinct tools:
- `GradeEssayFromRubricTool`: Tailored for grading written essays.
- `GradeCodeFromRubricTool`: Tailored for grading programming assignments.
"""
import json
import logging
from pydantic import ValidationError
from fairlib import AbstractTool, FinalGrade
from fairlib.core.interfaces.llm import AbstractChatModel

logger = logging.getLogger(__name__)

class GradeEssayFromRubricTool(AbstractTool):
    """
    A tool to generate a structured JSON grade for a written essay by synthesizing
    content, style, and fact-checking analyses.
    """
    name = "grade_essay_from_rubric"
    description = "Generates a structured JSON grade for an essay, synthesizing all provided analyses."
    
    # This prompt is a carefully engineered instruction set for the LLM. It constrains
    # the model to act as a data-entry assistant, reducing the chance of creative
    # or unformatted output.
    EXTRACTION_PROMPT_TEMPLATE = """
You are a meticulous teaching assistant filling out a JSON grading form for an essay. Your response MUST be ONLY the JSON object conforming to the schema. Evaluate the essay against each criterion using the rubric and all provided analyses.

**Grading Rubric:** {rubric}
**Content Analysis:** {content_feedback}
**Writing Style Analysis:** {style_feedback}
**Fact-Checking Results:** {fact_check_results}
**JSON Schema to Generate:** ```json
{schema}
```
**Full Essay to Grade:**
---
{essay}
---
Your JSON Output:
"""
    def __init__(self, llm: AbstractChatModel):
        self.llm = llm

    def use(self, tool_input: str) -> str:
        """
        Executes the structured JSON generation with a retry mechanism.

        Args:
            tool_input: A JSON string containing all necessary components
                        (essay, rubric, and various feedback strings).

        Returns:
            A JSON string of the validated FinalGrade object, or an error message.
        """
        logger.info("RubricAligner is generating final structured grade for essay.")
        max_retries = 2
        last_error = ""
        for attempt in range(max_retries):
            try:
                input_data = json.loads(tool_input)
                prompt = self.EXTRACTION_PROMPT_TEMPLATE.format(
                    schema=json.dumps(FinalGrade.model_json_schema(), indent=2),
                    **input_data
                )
                response_text = self.llm.chat([{"role": "system", "content": prompt}])
                
                # LLMs occasionally wrap their JSON output in markdown backticks.
                # This line robustly removes them if they exist.
                if response_text.strip().startswith("```json"):
                    response_text = response_text.strip()[7:-3]
                
                # Pydantic validates the structure and types of the JSON data.
                # If this line fails, it raises a ValidationError.
                validated_grade = FinalGrade.model_validate_json(response_text)
                return validated_grade.model_dump_json(indent=2)
            except (ValidationError, json.JSONDecodeError) as e:
                last_error = str(e)
                logger.warning(f"Structured essay grade validation failed (attempt {attempt + 1}/{max_retries}): {last_error}")
                if attempt == max_retries - 1:
                    logger.error("Final attempt to generate valid grade JSON failed.")
                    return f"Error: Failed to generate valid grade JSON after {max_retries} attempts. Last error: {last_error}"
            except Exception as e:
                logger.error(f"Unexpected error in GradeEssayFromRubricTool: {e}", exc_info=True)
                return "Error: An unexpected error occurred during final grading."
        return f"Error: Tool failed after all retries. Last error: {last_error}"

class GradeCodeFromRubricTool(AbstractTool):
    """
    A tool to generate a structured JSON grade for a programming assignment by
    synthesizing test results, static analysis, and logic reviews.
    """
    name = "grade_code_from_rubric"
    description = "Generates a structured JSON grade for a programming assignment."
    
    EXTRACTION_PROMPT_TEMPLATE = """
You are a teaching assistant filling out a JSON grading form for a programming assignment. Your response MUST be ONLY the JSON object.

**Grading Rubric:** {rubric}
**Test Results:** {test_results}
**Static Analysis:** {static_analysis}
**Logic & Efficiency Review:** {logic_review}
**JSON Schema to Generate:** ```json
{schema}
```
**Full Code Submission:**
---
{code}
---
Your JSON Output:
"""
    def __init__(self, llm: AbstractChatModel):
        self.llm = llm

    def use(self, tool_input: str) -> str:
        """
        Executes the structured JSON generation for the code grade.
        
        Args:
            tool_input: A JSON string containing all necessary components
                        (code, rubric, test results, and reviews).

        Returns:
            A JSON string of the validated FinalGrade object, or an error message.
        """
        logger.info("RubricAligner is generating final structured grade for code.")
        max_retries = 2
        last_error = ""
        for attempt in range(max_retries):
            try:
                input_data = json.loads(tool_input)
                prompt = self.EXTRACTION_PROMPT_TEMPLATE.format(
                    schema=json.dumps(FinalGrade.model_json_schema(), indent=2),
                    **input_data
                )
                response_text = self.llm.chat([{"role": "system", "content": prompt}])
                if response_text.strip().startswith("```json"):
                    response_text = response_text.strip()[7:-3]
                validated_grade = FinalGrade.model_validate_json(response_text)
                return validated_grade.model_dump_json(indent=2)
            except (ValidationError, json.JSONDecodeError) as e:
                last_error = str(e)
                logger.warning(f"Structured code grade validation failed (attempt {attempt + 1}/{max_retries}): {last_error}")
                if attempt == max_retries - 1:
                    logger.error("Final attempt to generate valid code grade JSON failed.")
                    return f"Error: Failed to generate valid grade JSON after {max_retries} attempts. Last error: {last_error}"
            except Exception as e:
                logger.error(f"Unexpected error in GradeCodeFromRubricTool: {e}", exc_info=True)
                return "Error: An unexpected error occurred during final grading."
        return f"Error: Tool failed after all retries. Last error: {last_error}"