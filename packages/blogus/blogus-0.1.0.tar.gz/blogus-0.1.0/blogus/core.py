"""
Core module for prompt engineering functionality.

This module provides the foundation for the prompt development lifecycle, including:
- Prompt execution using target LLMs
- Prompt analysis and evaluation using judge LLMs
- Fragment analysis for goal alignment
- Test case generation
- Goal inference

The module is designed to support the complete prompt engineering workflow:
1. Initial prompt creation
2. Analysis and evaluation
3. Iterative enhancement
4. Test dataset generation
5. Cross-model validation

Key Features:
- Separation of target models (for prompt execution) and judge models (for analysis)
- Support for multiple LLM providers through LiteLLM
- Structured analysis of prompt effectiveness
- Automated test case generation
"""

import os
import json
import re
from typing import List, Optional, Dict, Any
from enum import Enum
from dotenv import load_dotenv
from litellm import completion

# Load environment variables
load_dotenv()

# Define model enums for target models and judge models
class TargetLLMModel(str, Enum):
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    GPT_4 = "gpt-4o"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GROQ_LLAMA3_70B = "groq/llama3-70b-8192"
    GROQ_MIXTRAL_8X7B = "groq/mixtral-8x7b-32768"
    GROQ_GEMMA_7B = "groq/gemma-7b-it"


class JudgeLLMModel(str, Enum):
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    GPT_4 = "gpt-4o"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GROQ_LLAMA3_70B = "groq/llama3-70b-8192"
    GROQ_MIXTRAL_8X7B = "groq/mixtral-8x7b-32768"
    GROQ_GEMMA_7B = "groq/gemma-7b-it"


class Fragment:
    """Represents a fragment of a prompt with analysis results.
    
    A fragment is a section of a prompt that has been analyzed for its alignment
    with the overall goal and potential for improvement.
    
    Attributes:
        text (str): The text content of the fragment
        type (str): The type of fragment (instruction, context, example, or constraint)
        goal_alignment (int): Alignment score with the goal (1-5 scale)
        improvement_suggestion (str): Suggested improvements for better goal alignment
    """
    def __init__(
        self, text: str, type: str, goal_alignment: int, improvement_suggestion: str
    ):
        self.text = text
        self.type = type
        self.goal_alignment = goal_alignment
        self.improvement_suggestion = improvement_suggestion


class Log:
    """Represents a log message generated during prompt analysis.
    
    Logs provide information, warnings, or errors relevant to achieving the prompt's goal.
    
    Attributes:
        type (str): The type of log (info, warning, or error)
        message (str): The log message content
    """
    def __init__(self, type: str, message: str):
        self.type = type
        self.message = message


class Test:
    """Represents a test case for evaluating prompt performance.
    
    Test cases are generated to validate that prompts produce expected outputs
    for specific inputs, with relevance scoring based on the prompt's goal.
    
    Attributes:
        input (Dict[str, str]): Input variables and their values for the test
        expected_output (str): The expected output for the given input
        goal_relevance (int): Relevance of the test to achieving the prompt's goal (1-5 scale)
    """
    def __init__(
        self, input: Dict[str, str], expected_output: str, goal_relevance: int
    ):
        self.input = input
        self.expected_output = expected_output
        self.goal_relevance = goal_relevance


class PromptAnalysis:
    """Represents a comprehensive analysis of a prompt's effectiveness.
    
    Contains metrics and suggestions for improving a prompt's alignment with its goal
    and overall effectiveness.
    
    Attributes:
        overall_goal_alignment (int): Overall alignment with the goal (1-10 scale)
        suggested_improvements (List[str]): List of suggested improvements
        estimated_effectiveness (int): Estimated effectiveness in achieving the goal (1-10 scale)
        inferred_goal (Optional[str]): The inferred goal if not explicitly provided
        is_goal_inferred (bool): Whether the goal was inferred or explicitly provided
    """
    def __init__(
        self,
        overall_goal_alignment: int,
        suggested_improvements: List[str],
        estimated_effectiveness: int,
        inferred_goal: Optional[str] = None,
        is_goal_inferred: bool = False,
    ):
        self.overall_goal_alignment = overall_goal_alignment
        self.suggested_improvements = suggested_improvements
        self.estimated_effectiveness = estimated_effectiveness
        self.inferred_goal = inferred_goal
        self.is_goal_inferred = is_goal_inferred


def get_llm_response(model: str, prompt: str, max_tokens: int = 1000) -> str:
    """Get a response from the specified LLM using LiteLLM.
    
    This is the core function that interfaces with LLMs through LiteLLM's unified API.
    It handles the low-level communication with various LLM providers.
    
    Args:
        model (str): The LLM model to use (e.g., "gpt-4o", "claude-3-opus-20240229")
        prompt (str): The prompt to send to the model
        max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 1000.
        
    Returns:
        str: The response from the LLM as a string
        
    Example:
        >>> response = get_llm_response("gpt-4o", "Explain quantum computing in simple terms")
        >>> print(response)
        'Quantum computing is a type of computing that uses quantum bits...'
    """
    response = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def infer_goal(prompt: str, model: str) -> str:
    """Infer the goal of a prompt using an LLM.
    
    This function uses a judge model to analyze a prompt and determine its intended goal.
    Goal inference is a critical step in prompt evaluation when an explicit goal is not provided.
    
    The function uses a structured prompt to guide the judge model in extracting the goal,
    and expects a JSON response with the goal in a specific format.
    
    Args:
        prompt (str): The prompt to analyze for goal inference
        model (str): The judge LLM model to use for inference (e.g., "gpt-4o")
        
    Returns:
        str: The inferred goal as a string
        
    Example:
        >>> prompt = "You are an AI assistant that helps people find information about books."
        >>> goal = infer_goal(prompt, "gpt-4o")
        >>> print(goal)
        'Help users find information about books'
        
    Note:
        If the judge model fails to return properly formatted JSON, the function will
        fall back to returning the raw response text.
    """
    inference_prompt = f"""Given the following prompt, infer the likely goal or intention of the user:

Prompt: {prompt}

Provide a concise statement of the inferred goal in one sentence as a JSON dictionary with the key "goal" and the value being the inferred goal.
"""
    response = get_llm_response(model, inference_prompt)
    try:
        return json.loads(response)["goal"]
    except (json.JSONDecodeError, KeyError):
        # Fallback if JSON parsing fails
        return response.strip()


def analyze_fragments(
    prompt: str, judge_model: str, goal: Optional[str] = None
) -> List[Fragment]:
    """Analyze prompt fragments for goal alignment.
    
    This function breaks down a prompt into logical fragments and evaluates each one
    for its alignment with the prompt's goal. This granular analysis helps identify
    specific areas for improvement within complex prompts.
    
    Fragment types include:
    - Instruction: Direct guidance to the LLM
    - Context: Background information or setting
    - Example: Demonstrations of expected behavior
    - Constraint: Limitations or boundaries on responses
    
    Args:
        prompt (str): The prompt to analyze
        judge_model (str): The judge LLM model to use for analysis (e.g., "gpt-4o")
        goal (Optional[str], optional): The goal of the prompt. If not provided,
            it will be inferred using the judge model. Defaults to None.
            
    Returns:
        List[Fragment]: A list of Fragment objects with detailed analysis results
        
    Raises:
        ValueError: If the judge model response cannot be parsed as valid JSON
        
    Example:
        >>> prompt = "You are a helpful assistant. Answer questions clearly."
        >>> fragments = analyze_fragments(prompt, "gpt-4o")
        >>> for fragment in fragments:
        ...     print(f"Text: {fragment.text}")
        ...     print(f"Type: {fragment.type}")
        ...     print(f"Alignment: {fragment.goal_alignment}/5")
        ...     print(f"Suggestion: {fragment.improvement_suggestion}")
    """
    if goal is None:
        goal = infer_goal(prompt, judge_model)

    llm_prompt = f"""Analyze the following prompt for an LLM, keeping in mind the goal:

Prompt: {prompt}

Goal: {goal}

Divide the prompt into fragments and analyze each fragment. For each fragment, determine:
1. The type (instruction, context, example, or constraint)
2. How well it aligns with the goal (1-5, where 5 is perfectly aligned)
3. A suggestion for improvement to better align with the goal

Provide your analysis in the following JSON format without any other text:
{{
  "fragments": [
    {{
      "text": "fragment text",
      "type": "fragment type",
      "goal_alignment": alignment_score,
      "improvement_suggestion": "suggestion to better align with goal"
    }},
    ...
  ]
}}
"""

    response = get_llm_response(judge_model, llm_prompt)
    try:
        analysis = json.loads(response)
        return [Fragment(**fragment) for fragment in analysis["fragments"]]
    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"Failed to parse fragment analysis: {e}")


def analyze_logs(prompt: str, judge_model: str, goal: Optional[str] = None) -> List[Log]:
    """Analyze prompt for potential issues and generate logs.
    
    This function generates structured log messages (info, warning, error) that highlight
    potential issues or areas of concern in a prompt. Logs are focused on aspects that
    are relevant to achieving the prompt's goal.
    
    Log types:
    - Info: General information about the prompt structure or design
    - Warning: Potential issues that may affect performance
    - Error: Clear problems that will likely impact results
    
    Args:
        prompt (str): The prompt to analyze
        judge_model (str): The judge LLM model to use for analysis (e.g., "gpt-4o")
        goal (Optional[str], optional): The goal of the prompt. If not provided,
            it will be inferred using the judge model. Defaults to None.
            
    Returns:
        List[Log]: A list of Log objects with analysis results
        
    Raises:
        ValueError: If the judge model response cannot be parsed as valid JSON
        
    Example:
        >>> prompt = "Answer questions."
        >>> logs = analyze_logs(prompt, "gpt-4o")
        >>> for log in logs:
        ...     print(f"[{log.type.upper()}] {log.message}")
        [WARNING] The prompt is very brief and may not provide sufficient guidance
        [INFO] Consider adding specific examples of desired response formats
    """
    if goal is None:
        goal = infer_goal(prompt, judge_model)

    llm_prompt = f"""Analyze the following prompt for an LLM, keeping in mind the goal:

Prompt: {prompt}

Goal: {goal}

Generate a list of logs (info, warnings, or errors) based on the changes being made to the prompt. Focus on aspects that are relevant to achieving the goal.

Provide your analysis in the following JSON format without any other text:
{{
  "logs": [
    {{
      "type": "info/warning/error",
      "message": "log message relevant to achieving the goal"
    }},
    ...
  ]
}}
"""

    response = get_llm_response(judge_model, llm_prompt)
    try:
        analysis = json.loads(response)
        return [Log(**log) for log in analysis["logs"]]
    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"Failed to parse log analysis: {e}")


def analyze_prompt(
    prompt: str, judge_model: str, goal: Optional[str] = None
) -> PromptAnalysis:
    """Perform a comprehensive analysis of a prompt.
    
    This function provides a holistic evaluation of a prompt's effectiveness in achieving
    its intended goal. It returns a detailed analysis including overall alignment scores,
    specific improvement suggestions, and effectiveness estimates.
    
    The analysis includes:
    1. Overall goal alignment (1-10 scale)
    2. Specific suggestions for improvement
    3. Estimated effectiveness (1-10 scale)
    4. Goal inference (if not explicitly provided)
    
    Args:
        prompt (str): The prompt to analyze
        judge_model (str): The judge LLM model to use for analysis (e.g., "gpt-4o")
        goal (Optional[str], optional): The goal of the prompt. If not provided,
            it will be inferred using the judge model. Defaults to None.
            
    Returns:
        PromptAnalysis: A PromptAnalysis object with comprehensive analysis results
        
    Raises:
        ValueError: If the judge model response cannot be parsed as valid JSON
        
    Example:
        >>> prompt = "You are a helpful assistant. Answer questions clearly."
        >>> analysis = analyze_prompt(prompt, "gpt-4o")
        >>> print(f"Alignment: {analysis.overall_goal_alignment}/10")
        >>> print(f"Effectiveness: {analysis.estimated_effectiveness}/10")
        >>> for suggestion in analysis.suggested_improvements:
        ...     print(f"Suggestion: {suggestion}")
    """
    is_goal_inferred = False
    if goal is None:
        goal = infer_goal(prompt, judge_model)
        is_goal_inferred = True

    llm_prompt = f"""Analyze the following prompt for an LLM, keeping in mind the {'inferred' if is_goal_inferred else 'provided'} goal:

Prompt: {prompt}

{'Inferred' if is_goal_inferred else 'Provided'} Goal: {goal}

Provide an overall analysis including:
1. Overall alignment of the prompt with the goal (1-10)
2. List of suggested improvements to better achieve the goal
3. Estimated effectiveness of the prompt in achieving the goal (1-10)

Provide your analysis in the following JSON format without any other text:
{{
  "overall_goal_alignment": overall_alignment_score,
  "suggested_improvements": ["improvement1", "improvement2", ...],
  "estimated_effectiveness": effectiveness_score,
  "inferred_goal": "{goal if is_goal_inferred else ''}",
  "is_goal_inferred": {str(is_goal_inferred).lower()}
}}
"""

    response = get_llm_response(judge_model, llm_prompt)
    try:
        analysis = json.loads(response)
        return PromptAnalysis(**analysis)
    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"Failed to parse prompt analysis: {e}")


def generate_test(prompt: str, judge_model: str, goal: Optional[str] = None) -> Test:
    """Generate a test case for a prompt.
    
    This function generates structured test cases to validate prompt performance.
    Test cases include input variables, expected outputs, and relevance scoring
    based on the prompt's goal.
    
    The function automatically identifies variables in the prompt (marked with
    curly braces like {variable_name}) and generates appropriate test values.
    
    Args:
        prompt (str): The prompt to generate a test for
        judge_model (str): The judge LLM model to use for test generation (e.g., "gpt-4o")
        goal (Optional[str], optional): The goal of the prompt. If not provided,
            it will be inferred using the judge model. Defaults to None.
            
    Returns:
        Test: A Test object with the generated test case
        
    Raises:
        ValueError: If the judge model response cannot be parsed as valid JSON
        
    Example:
        >>> prompt = "Translate the following English text to French: {text}"
        >>> test_case = generate_test(prompt, "gpt-4o")
        >>> print(f"Input: {test_case.input}")
        >>> print(f"Expected: {test_case.expected_output}")
        >>> print(f"Relevance: {test_case.goal_relevance}/5")
    """
    if goal is None:
        goal = infer_goal(prompt, judge_model)

    variables = re.findall(r"\{([^}]+)\}", prompt)

    llm_prompt = f"""Generate a test case for the following LLM prompt, keeping in mind the goal:

Prompt: {prompt}

Goal: {goal}

Variables found in the prompt: {', '.join(variables)}

Provide a test case that is relevant to achieving the goal. Use the following JSON format:
{{
  "input": {{
    "variable1": "value1",
    "variable2": "value2",
    ...
  }},
  "expected_output": "expected output for the test case",
  "goal_relevance": relevance_score
}}

The input should include values for all variables found in the prompt.
The goal_relevance score should be from 1-5, where 5 means the test case is highly relevant to achieving the goal.
"""

    response = get_llm_response(judge_model, llm_prompt)
    try:
        test_data = json.loads(response)
        return Test(**test_data)
    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"Failed to parse test generation: {e}")


def execute_prompt(prompt: str, target_model: str) -> str:
    """Execute a prompt using the specified target LLM.
    
    This function sends a prompt to a target LLM and returns the model's response.
    It's the primary interface for testing prompts in real-world scenarios.
    
    Args:
        prompt (str): The prompt to execute
        target_model (str): The target LLM model to use for execution (e.g., "gpt-4o")
        
    Returns:
        str: The response from the LLM as a string
        
    Example:
        >>> prompt = "Explain quantum computing in simple terms."
        >>> response = execute_prompt(prompt, "gpt-4o")
        >>> print(response)
        'Quantum computing is a type of computing that uses quantum bits...'
    """
    return get_llm_response(target_model, prompt)
