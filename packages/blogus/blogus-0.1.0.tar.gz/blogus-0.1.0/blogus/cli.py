"""
Command-line interface for Blogus.
"""

import click
from blogus.core import (
    TargetLLMModel,
    JudgeLLMModel,
    analyze_prompt,
    analyze_fragments,
    analyze_logs,
    generate_test,
    execute_prompt,
    infer_goal,
)


@click.group()
def cli():
    """Blogus: A tool for crafting, analyzing, and perfecting AI prompts."""
    pass


@cli.command()
@click.argument("prompt", type=str)
@click.option(
    "--target-model",
    type=click.Choice([m.value for m in TargetLLMModel]),
    default=TargetLLMModel.GPT_4,
    help="Target LLM model to use for prompt execution",
)
@click.option(
    "--judge-model",
    type=click.Choice([m.value for m in JudgeLLMModel]),
    default=JudgeLLMModel.GPT_4,
    help="Judge LLM model to use for analysis",
)
@click.option(
    "--goal",
    type=str,
    default=None,
    help="Goal for the prompt (will be inferred if not provided)",
)
def analyze(prompt, target_model, judge_model, goal):
    """Analyze a prompt for effectiveness and alignment with a goal."""
    click.echo(f"Analyzing prompt with judge model {judge_model}...")

    # Perform analysis
    analysis = analyze_prompt(prompt, judge_model, goal)

    click.echo("\nPrompt Analysis Results:")
    click.echo("=" * 50)
    click.echo(f"Overall Goal Alignment: {analysis.overall_goal_alignment}/10")
    click.echo(f"Estimated Effectiveness: {analysis.estimated_effectiveness}/10")

    if analysis.is_goal_inferred:
        click.echo(f"Inferred Goal: {analysis.inferred_goal}")

    click.echo("\nSuggested Improvements:")
    for i, improvement in enumerate(analysis.suggested_improvements, 1):
        click.echo(f"  {i}. {improvement}")


@cli.command()
@click.argument("prompt", type=str)
@click.option(
    "--target-model",
    type=click.Choice([m.value for m in TargetLLMModel]),
    default=TargetLLMModel.GPT_4,
    help="Target LLM model to use for prompt execution",
)
@click.option(
    "--judge-model",
    type=click.Choice([m.value for m in JudgeLLMModel]),
    default=JudgeLLMModel.GPT_4,
    help="Judge LLM model to use for analysis",
)
@click.option(
    "--goal",
    type=str,
    default=None,
    help="Goal for the prompt (will be inferred if not provided)",
)
def fragments(prompt, target_model, judge_model, goal):
    """Analyze prompt fragments for goal alignment."""
    click.echo(f"Analyzing prompt fragments with judge model {judge_model}...")

    # Analyze fragments
    fragments = analyze_fragments(prompt, judge_model, goal)

    click.echo("\nFragment Analysis Results:")
    click.echo("=" * 50)
    for i, fragment in enumerate(fragments, 1):
        click.echo(f"\nFragment {i}:")
        click.echo(f"  Text: {fragment.text}")
        click.echo(f"  Type: {fragment.type}")
        click.echo(f"  Goal Alignment: {fragment.goal_alignment}/5")
        click.echo(f"  Improvement Suggestion: {fragment.improvement_suggestion}")


@cli.command()
@click.argument("prompt", type=str)
@click.option(
    "--target-model",
    type=click.Choice([m.value for m in TargetLLMModel]),
    default=TargetLLMModel.GPT_4,
    help="Target LLM model to use for prompt execution",
)
@click.option(
    "--judge-model",
    type=click.Choice([m.value for m in JudgeLLMModel]),
    default=JudgeLLMModel.GPT_4,
    help="Judge LLM model to use for analysis",
)
@click.option(
    "--goal",
    type=str,
    default=None,
    help="Goal for the prompt (will be inferred if not provided)",
)
def logs(prompt, target_model, judge_model, goal):
    """Generate logs for a prompt."""
    click.echo(f"Generating logs with judge model {judge_model}...")

    # Generate logs
    logs = analyze_logs(prompt, judge_model, goal)

    click.echo("\nPrompt Logs:")
    click.echo("=" * 50)
    for log in logs:
        click.echo(f"[{log.type.upper()}] {log.message}")


@cli.command()
@click.argument("prompt", type=str)
@click.option(
    "--target-model",
    type=click.Choice([m.value for m in TargetLLMModel]),
    default=TargetLLMModel.GPT_4,
    help="Target LLM model to use for prompt execution",
)
@click.option(
    "--judge-model",
    type=click.Choice([m.value for m in JudgeLLMModel]),
    default=JudgeLLMModel.GPT_4,
    help="Judge LLM model to use for analysis",
)
@click.option(
    "--goal",
    type=str,
    default=None,
    help="Goal for the prompt (will be inferred if not provided)",
)
def test(prompt, target_model, judge_model, goal):
    """Generate a test case for a prompt."""
    click.echo(f"Generating test case with judge model {judge_model}...")

    # Generate test
    test_case = generate_test(prompt, judge_model, goal)

    click.echo("\nGenerated Test Case:")
    click.echo("=" * 50)
    click.echo("Input:")
    for key, value in test_case.input.items():
        click.echo(f"  {key}: {value}")
    click.echo(f"\nExpected Output: {test_case.expected_output}")
    click.echo(f"Goal Relevance: {test_case.goal_relevance}/5")


@cli.command()
@click.argument("prompt", type=str)
@click.option(
    "--target-model",
    type=click.Choice([m.value for m in TargetLLMModel]),
    default=TargetLLMModel.GPT_4,
    help="Target LLM model to use for prompt execution",
)
def execute(prompt, target_model):
    """Execute a prompt with the specified target LLM."""
    click.echo(f"Executing prompt with target model {target_model}...")

    # Execute prompt
    result = execute_prompt(prompt, target_model)

    click.echo("\nExecution Result:")
    click.echo("=" * 50)
    click.echo(result)


@cli.command()
@click.argument("prompt", type=str)
@click.option(
    "--judge-model",
    type=click.Choice([m.value for m in JudgeLLMModel]),
    default=JudgeLLMModel.GPT_4,
    help="Judge LLM model to use for analysis",
)
def goal(prompt, judge_model):
    """Infer the goal of a prompt."""
    click.echo(f"Inferring goal with judge model {judge_model}...")

    # Infer goal
    inferred_goal = infer_goal(prompt, judge_model)

    click.echo("\nInferred Goal:")
    click.echo("=" * 50)
    click.echo(inferred_goal)


if __name__ == "__main__":
    cli()
